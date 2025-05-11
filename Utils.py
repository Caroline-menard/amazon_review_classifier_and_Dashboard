import re
import string
import pandas as pd
from textblob import TextBlob
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FunctionTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier
import spacy
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

LABEL_COLUMNS =  [
        "non_tenu", "produit_non_conforme", "mauvaise_qualite", "produit_endommage",
        "retour_client", "produit_dangereux", "aucun_probleme", "autre_probleme", "sav_saller_probleme"
    ]
PATH_LABELISED_SET = "Model_elements/final_labeled.csv"   #labelised_set2.csv"

# ==== Custom preprocessing classes ====
class Preprocessor(BaseEstimator, TransformerMixin):
    """Clean and format the input DataFrame."""
    def fit(self, X, y=None):
        return self

    def transform(self, df):
        df = df.copy()
        df.fillna("", inplace=True)
        df["revue"] = df["title"] + ". " + df["text"]
        return df[df["revue"] != ". "]


class LabelCorrection(BaseEstimator, TransformerMixin):
    """Apply correction rules after model prediction."""
    def fit(self, X, y=None):
        return self

    def transform(self, df):
        df = df.copy()
        other_labels = [label for label in LABEL_COLUMNS if label not in ["retour_client",
                                                                          "aucun_probleme"]]
        df.loc[df["rating"].isin([4, 5]), "aucun_probleme"] = 1
        for label in other_labels:
            df.loc[df["rating"].isin([4, 5]), label] = 0
        all_labels = LABEL_COLUMNS
        no_label_mask = (df[all_labels].sum(axis=1) == 0) & df["rating"].isin([1, 2, 3])
        df.loc[no_label_mask, "autre_probleme"] = 1
        return df

# ==== Feature extraction helpers ====
def wrap_function(func, *args):
    return FunctionTransformer(lambda col: col.apply(lambda x: func(x, *args)).to_numpy().reshape(-1, 1), validate=False)

pos_voc = ['great', 'love', 'easy', 'soft', 'perfect', 'best',  'happy',
            'amazing', 'beautiful', 'highly', 'ever',  'absolutely', 'loves'
           , 'wonderful','excellent',  'loved', 'favorite',"good",
            'exactly',  'awesome','perfectly',  'pleased',  'thank', 'glad',
              'fantastic','thanks',  'compliments','silky','gorgeous',  'durable','wow']

neg_voc = ['annoyed', 'awful', 'balls', 'beware', 'broke', 'cheaply',
           'chipped', 'chunks', 'crap', 'defeats', 'defective', 
           'disapointed', 'disappointed', 'disappointing', 'disappointment',
           'disgusting', 'expired', 'fail', 'flaked', 'formaldehyde',
           'garbage', 'hopes', 'horrible', 'impossible', 'ineffective',
           'joke', 'junk', 'lies', 'limp', 'matted', 'misleading',
           'nope', 'peeled', 'poor', 'poorly', 'refund', 'refunded',
           'return', 'returned', 'returning', 'rip', 'ripped', 'rotten',
           'scam''scammmer' ,'shame', 'terrible', 'threads', 'threw', 'trash',
           'trashed', 'ugh', 'unhappy', 'unnatural', 'unusable', 'useless',
           'waste', 'wasted', 'worse', 'worst', 'worthless', 'wrong']



quality_expressions = ['awful', 'bad', 'cheap ', 'cheaply','expensive',
                       'crap', 'dirty', 'garbage', 'horrible', 'junk',
                       'low', 'matted', 'not even worth', 'not worth',
                       'over priced', 'overpriced', 'poor', 'poorly',
                       'pricy', 'stink', 'stinking', 'stinks', 'stinky',
                       'terrible', 'trash',"bad smell",'awful smell',
                      'horrible smell']


dammage_expr = ['a mess', 'arrived dry', 'been used', 'break', 'breaken', 'breakes',
                'breaks''broke', 'broken', 'brokes', 'busted', 'came apart',
                'came dry','come apart','cracked','stopped functioning','flimsy'
                ,' flimsey', 'cracks', 'crushed', 'damage', 'damaged', 'defective', 'destroyed', 
                'disintegrated', 'dried out', 'dried up', 'expired', 'fall apart', 'fall off', 
                'fallen off', 'falling apart', 'falling off', 'falls apart', 'falls off',
                'fell apart', 'fell off', 'fell out', 'fragile', 'leak',
                'leaked', 'leaking', 'leaks', 'malfunction', 'matted', 'melted', 'melting', 
                'missing', 'poor condition', 'rip out', 'ripped', 'ripped', 'rips out',
                'rotten', 'shattered', 'soaked', 'split', 'splitting', 'tear', 'unusable', 
                'watered']

side_effect_expr = ['acne', 'aggressive', 'allergic', 'allergy', 'bad reaction', 'blister',
                    'breakout','burnt','sore', 'cancer','carcinogenic',
                    'breakouts', 'bruising', 'bumps', 'burn', 'burned', 'burning', 'burns',
                    'chemical', 'contaminated', 'cramps', 'damaged my', 'damages', 'dangerous',
                    'dermatitis', 'diarrhea', 'dizziness', 'dried', 'dry', 'dryness', 'eczema',
                    'fainting', 'fatigue', 'flaking', 'formaldehyde', 'harmful', 'harsh', 
                    'headache', 'hives', 'hurt', 'hurts', 'inflamed', 'inflammation', 'insomnia',
                    'irritated', 'irritation', 'itch', 'itching', 'itchy', 'migraine', 'nausea',
                    'outch', 'pain', 'painful', 'peeling', 'pimples', 'psoriasis', 'rash', 'red',
                    'redness', 'rough', 'ruined', 'scratchier', 'scratchy', 'severe reaction',
                    'stomachache', 'swelling','swollen', 'swollenstinging', 'toxic', 'unsafe',
                    'vomiting']
to_replace = {
    "break out":"breakout",
    "brokes out":"breakout",
    "breaks out":"breakout",
    "broke out": "breakout",
    "breaking out": "breakout",
    "pimples":"breakout",
    "pimple":"breakout",
    " no ":" not ",
    "$":"dollar "
    }
    
def neg_emojis_counter(texte):
    emoji_pattern = re.compile(
        "[\U0001F631"  # :cri:
        "\U0001F4A3"  # :bombe:
        "\U0001F621"  # :rage:
        "\U0001F620"  # :en_colère:
        "\U0001F612"  # :pas_marrant:
        "\U0001F61E"  # :déçu:
        "\U0001F622"  # :pleurs:
        "\U0001F62D"  # :sanglot:
        "\U0001F922"  # :visage_envie_de_vomir:
        "\U0001F92E"  # :visage_qui_vomit:
        "]"
    )
    return len(emoji_pattern.findall(str(texte)))

def pos_emojis_counter(texte):
    emoji_pattern = re.compile(
        "[\u263A"       # :détendu:
        "\U0001F60A"    # :rougir:
        "\U0001F970"    # :visage_souriant_3_coeurs:
        "\U0001F60D"    # :yeux_en_cœur:
        "\U0001F618"    # :envoie_un_bisou:
        "\U0001F642"    # :visage_légèrement_souriant:
        "\U0001F603"    # :smiley:
        "\U0001F604"    # :sourire:
        "\U0001F601"    # :sourire_et_yeux_rieurs:
        "\U0001F917"    # :câlin:
        "\u2764"        # :cœur:
        "\U0001F495"    # :deux_cœurs:
        "\U0001F496"    # :cœur_scintillant:
        "]"
    )
    return len(emoji_pattern.findall(str(texte)))

def regrouped_rating(rating):
    '''allows you to group the notes and smooth out the differences in the notes'''
    if rating in [5,4]:
        return 2
    if rating ==3:
        return 1
    return 0

def count_trigger(sentence, vocabulary):
    '''Allows counting iterations of specific vocabulary. 
    input: text and word list. 
    Output: int'''
    sentence = sentence.lower()
    return sum([int(i in sentence) for i in vocabulary])

def replace_numbers(text):
    # 1. Remplace les chiffres (ex: 42, 3.14, etc.)
    text = re.sub(r'\b\d+([.,]\d+)?\b', 'number', text)

    # 2. Remplace les nombres écrits en toutes lettres (anglais, communs)
    number_words = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
        'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
        'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
        'eighty', 'ninety', 'hundred', 'thousand', 'million', 'billion'
    ]

    pattern = r'\b(?:' + '|'.join(number_words) + r')(?:[-\s](?:' + '|'.join(number_words) + r'))*\b'
    text = re.sub(pattern, 'number', text, flags=re.IGNORECASE)

    return text 
def preprocess_text(text):
    # Convert to lower  
    text = text.lower().replace("<br />","").replace("!"," exclam")
    for u,v in to_replace.items():
        text = text.replace(u,v)
    # Remove  punctuation 
    text = text.translate(str.maketrans({p: ' ' for p in string.punctuation}))
    # Remove emojis  
    text = re.sub(r'[^\x00-\x7F]+', '', text) 
     # Replace digit by "number":
    text = replace_numbers(text)
    
    # Use a regex to remove single letters 
    text = re.sub(r'\b[a-zA-Z]\b', '', text)
    # Remove multiple spaces caused by deletion  
    text = re.sub(r'\s+', ' ', text).strip()
    # Tokenisation + lemmatisation + stopword removal (sans retirer les négations)
    doc = nlp(text)
    stopwords = set(nlp.Defaults.stop_words) - {"not", "no", "nor", "don", "didn", "won", 
                                                "shouldn","off","can","wasn","only",
                                                "ain","last","than","first","enough",
                                               "there","back","breakout",'too'}
    tokens = [token.lemma_ for token in doc if token.lemma_ not in stopwords and token.lemma_.isalpha()]
    return ' '.join(tokens)

def get_sentiment(text):
    '''allows you to obtain a polarity score between -1 and 1 
    (1: the text is very positive, -1: the text is very negative). 
    input: Text. 
    output: Polarity score'''
    analysis = TextBlob(text)
    return analysis.sentiment.polarity 

def track_trigger(text, list_expr):
    text = text.lower()
    text = text.translate(str.maketrans({p: ' ' for p in string.punctuation}))
    for u, v in to_replace.items():
        text = text.replace(u, v)
    # split the text
    tokens = text.split()
    total= sum(1 for token in tokens if token in list_expr)
    for exp in list_expr: #test multi word expression
        if len(exp.split(" "))>1 and exp in text:
            total+=1
    # Count the number of words in the list
    return total


pattern_return_refund = re.compile(
    r'\b('
    r'(return(ed|ing|s|able)?|exchanged)(\s+them|\s+it)?'           # return, returned, returning 
    r'|'
    r'sent(ing|s)?\s+(this|them\s+|it\s+)?back'                          # sent it back ou sent back
    r'|'
    r'send(ing|s)?\s+(this|them\s+|it\s+)?back'                          # send it back ou send back
    r'|'
    r'(want|would\s+like|ask|asking)\s+(for\s+)?(a\s+)?refund'  # want/ask for a refund
    r'|'
    r'refund(s|ed|ing|able)?'                              # refund, refunded, refunding
    r'|'
    r'reimburs(e|ed|ing|able)?'
    r'|'
    r'(replaced|repay|money\s+back)'
    r'|'
    r'(want|like|get)\s+(a\s+)?replacement'
    r')\b',
    flags=re.IGNORECASE
)

pattern_non_conformity = re.compile(
    r"\b("

    # 1. as described / as pictured / as advertised
    r"(not|don't|different)?(\w+\s+){0,4}?(as|than|was)\s+(described|pictured|advertised|advertising|photographed|depicted|displayed)"
    r"|"

    # 2. like the picture / like on tv
    r"like\s+(on\s+)?(the\s+)?(description|pic|pics|pictures|picture|photo|photos|advertising|tv|pictured|advertised|advertising)"
    r"|"

    # 3. described as / pictured as
    r"(described|pictured|advertised|advertising)\s+as"
    r"|"

    # 4. shown in/on the picture / photo / etc.
    r"(shown|described|match)\s+(in|on)\s+(the\s+)?(pic|pics|pictures|picture|photo|photos|advertising|tv|pictured|advertised|description)"
    r"|"

    r"(not|don't)\s(\w+\s+){0,2}?(match|matching)\s+(the\s+)?(pic|pics|pictures|picture|photo|photos|advertising|tv|pictured|advertised|description)"
    r"|"
    # 5. misleading / scam
    r"tampered|fraud|lie(s|d)?|fooled|innacurate|knockoff|cheat(s|ed)?|misleading|Imitation|scam|fake|rip\s+off|ripoff|way\s+off|counterfeit"
     r"|"
    # 5. incomplete
    r"incomplete|not\s+complete|missing"
    r"|"

    # 6. Not what I expected / Not like I expected
    r"not\s+(what|like)\s+(i\s+)?expected"
    r"|"

    # 7. Looks nothing like [photo/etc.]
    r"looks?\s+nothing\s+like"
    r"|"
    r"not\s(as+|the\s+)?(right|good|original|real)\s+(color|size|product|item|fragrance)(s)?"
    r"|"
    r"(wrong)\s+(color|size|product|item|fragrance)(s)?"
    r"|"
    # 8. Not [optional modifier] as described/pictured/etc.
    r"not\s+(\w+\s+){0,2}?(like\s+|as\s+)(the\s+)?(description|shown|pic|pics|pictures|picture|photo|photos|advertising|tv|pictured|advertised|description)"

    r")\b",
    re.IGNORECASE
)

pattern_broken_promise = re.compile(
    r'\b('
    r"haven't\s+seen\s+too\s+much\s+improvement"
    r'|'
    r'(no\s+)?(any\s+)?(improvement|result(s)?)'
    r'|'
    r"(does\s+not|didn't|don't|not)\s+do\s+(what\s+it\s+says|much)"
    r'|'
    r'not\s+(do\s+)?what\s+(they|it)\s+(say(s)?|claim(s)?|promise(s)?|pretend(s)?)'
    r'|'
    r"claiming\s+that|(didn't|doesn't|does\s+not)\s+work(s)?"
    r'|'
    r"(ineffective|useless|(does|did)\s+nothing)|(doesn't|didn't)\s+do\s+anything"
    r'|'
    r'not\s+effective'
    r'|'
    r"(not|didn't|don't)\s+(notice|see)\s+any\s+(\w+\s+){0,2}?(difference|result|effect(s)?)"
    r'|'
    r'contrary\s+to\s+(their|the)\s+(marketing\s+)?claim(s)?'
    r'|'
    r'did\s+not\s+address'
    r'|'
    r'works\s+slightly'
    r'|'
    r'not\s+perform\s+well'
    r'|'
    r'zero\s+benefit'
    r'|'
    r'works\s+a\s+little'
    r'|'
    r'got\s+any\s+results?'
    r'|'
    r'not\s+as\s+\w+(?:\s+\w+)*\s+as\s+(promised|advertised|expected|claimed|pretend)'
    r')\b',
    flags=re.IGNORECASE
)

def track_regex(text,pattern):
    text = text.lower().replace("’", "'")
    if pattern.search(text):
        return 1
    else:
        return 0
    
    #===========Pipeline=============
    
text_pipeline = Pipeline([
        ('preprocess', FunctionTransformer(lambda col: col.apply(preprocess_text), validate=False)),
        ('tfidf', TfidfVectorizer( 
            ngram_range=(1, 3),     # unigrams + bigrams+ trigrams
            max_features=None,#,     # ou moins selon ton dataset
            stop_words=None,        # tu as déjà fait le préprocessing
            min_df=2,               # on garde ce qui est fréquent
            max_df=0.8  )),        # sans être trop fréquent    
        ('svd', TruncatedSVD(n_components=20))
    ])

numeric_features = ColumnTransformer(transformers=[
        ('neg_emojis', wrap_function(neg_emojis_counter), 'revue'),
        ('pos_emojis', wrap_function(pos_emojis_counter), 'revue'),
        ('sentiment', wrap_function(get_sentiment), 'revue'),
        ('pos_trigger', wrap_function(count_trigger, pos_voc), 'revue'),
        ('neg_trigger', wrap_function(count_trigger, neg_voc), 'revue'),
        ('return_trigger',wrap_function(track_regex,pattern_return_refund), 'revue'),
        ('quality_triger',wrap_function(track_trigger,quality_expressions), 'revue'),
        ('broken_triger',wrap_function(track_trigger,dammage_expr), 'revue'),
        ('side_effect_triger',wrap_function(track_trigger,side_effect_expr), 'revue'),
        ('conformity_trigger',wrap_function(track_regex,pattern_non_conformity), 'revue'),
        ('claims_trigger',wrap_function(track_regex,pattern_broken_promise), 'revue'),
        ('grouped_rating', wrap_function(regrouped_rating), 'rating')
    ])

scaled_numeric_pipeline = Pipeline([
        ('features', numeric_features),
        ('scaler', StandardScaler())
    ])

final_features = ColumnTransformer(transformers=[
        ('text_features', text_pipeline, 'revue'),
        ('scaled_numeric', scaled_numeric_pipeline, ['revue', 'rating'])
    ])

model = MultiOutputClassifier(XGBClassifier(
            n_jobs=1,
            use_label_encoder=False,  # pour éviter le warning
            eval_metric='logloss',   # évite erreur pour multiclass
            random_state=42,
            verbosity=0,
            n_estimators = 100,
            subsample = 0.8,
            colsample_bytree = 0.8,
            max_depth = 3,
            learning_rate = 0.15
        )
                             )

full_pipeline = Pipeline(steps=[
        ('features', final_features),
        ('model', model)
    ])
    
# ==== Pipeline builder ====
def create_fitted_pipeline(df_train=None):
    df_train = df_train or pd.read_csv(PATH_LABELISED_SET,index_col=0)
    df_train = Preprocessor().transform(df_train)
    X_train = df_train[["revue", "rating"]]
    y_train = df_train[LABEL_COLUMNS]
    full_pipeline.fit(X_train, y_train)
    return full_pipeline

def predict_and_correct(df_to_predict, fitted_pipeline):
    df_input = Preprocessor().transform(df_to_predict)
    X_pred = df_input[["revue", "rating"]]
    y_pred = fitted_pipeline.predict(X_pred)
    y_pred_df = pd.DataFrame(y_pred, columns=LABEL_COLUMNS, index=df_input.index)
    result = pd.concat([df_input, y_pred_df], axis=1)
    corrected = LabelCorrection().transform(result)
    return corrected
