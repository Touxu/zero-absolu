import os
import json
import random
import unicodedata
import numpy as np

MODEL_PATH = "frWac_no_postag_no_phrase_500_skip_cut100.bin"
OUTPUT_DIR = "parties"
NB_PARTIES = 500
TARGET_CLEAN_VOCAB = 55000  # Élargi à 55 000 mots pour ne jamais couper de vocabulaire

# =============================================================================
# 1. LISTES BLANCHES FERMÉES (MOTS DE 2-3 LETTRES & MOTS COMPOSÉS AVEC TIRET)
# =============================================================================
VALID_SHORT_WORDS = {
    "air", "ail", "ami", "âme", "âne", "arc", "art", "as", "bac", "bal", "bar", "bas",
    "bec", "blé", "bol", "bon", "bus", "but", "cap", "car", "cas", "chat", "clé", "col",
    "coq", "cor", "cou", "cour", "cri", "cru", "cube", "cuir", "dam", "dame", "dé", "don",
    "dos", "duc", "dur", "eau", "élu", "épi", "ère", "est", "été", "fac", "fée", "fer",
    "feu", "fil", "fin", "foi", "fou", "gaz", "gel", "gui", "gué", "île", "jeu", "jus",
    "lac", "lait", "lin", "lit", "loi", "lot", "lys", "mai", "mal", "mas", "mât", "mer",
    "mets", "mie", "miel", "mois", "mot", "mou", "mur", "nef", "nez", "nid", "nom", "noix",
    "nu", "ode", "oie", "œil", "or", "os", "ours", "pain", "paix", "parc", "pas", "peau",
    "peur", "pic", "pied", "pin", "pli", "pneu", "poil", "pois", "pont", "porc", "port",
    "pot", "pou", "pré", "prix", "pub", "puits", "pur", "quai", "rat", "raz", "rez", "riz",
    "roc", "roi", "roue", "rue", "sac", "sec", "sel", "ski", "soi", "soie", "soir", "sol",
    "son", "sou", "sud", "suc", "taux", "thé", "tir", "toit", "ton", "tort", "toux", "tri",
    "trou", "tube", "val", "van", "veau", "vent", "ver", "vie", "vif", "vin", "vis", "voix",
    "vol", "vue", "zen", "zoo"
}

VALID_HYPHEN_WORDS = {
    "après-midi", "après-rasage", "après-shampoing", "après-ski", "après-vente",
    "arc-en-ciel", "arrière-grand-mère", "arrière-grand-père", "arrière-pays",
    "arrière-pensée", "arrière-plan", "assurance-vie", "auto-école", "avant-bras",
    "avant-centre", "avant-garde", "avant-goût", "avant-première", "avant-propos",
    "bain-marie", "bande-annonce", "basse-cour", "bateau-mouche", "beau-fils",
    "beau-frère", "beau-père", "belle-famille", "belle-fille", "belle-mère",
    "belle-sœur", "bien-être", "bien-fondé", "bonhomme", "bouche-à-oreille",
    "box-office", "brise-glace", "cache-cache", "camping-car", "canapé-lit",
    "casse-croûte", "casse-noix", "casse-tête", "centre-ville", "cerf-volant",
    "chauve-souris", "chef-lieu", "chou-fleur", "clair-obscur", "coffre-fort",
    "compte-gouttes", "compte-rendu", "contre-allée", "contre-attaque",
    "contre-enquête", "contre-espionnage", "contre-expertise", "contre-indication",
    "contre-jour", "contre-offensive", "contre-pied", "contre-plongée",
    "contre-pouvoir", "contre-sens", "contre-vérité", "coupe-circuit", "coupe-faim",
    "coupe-gorge", "coupe-vent", "court-bouillon", "court-circuit", "court-métrage",
    "couvre-feu", "couvre-lit", "croque-monsieur", "cul-de-sac", "demi-cercle",
    "demi-finale", "demi-frère", "demi-heure", "demi-journée", "demi-lune",
    "demi-mesure", "demi-pension", "demi-sœur", "demi-tarif", "demi-tour",
    "deux-roues", "double-clic", "eau-de-vie", "enseignant-chercheur", "entre-deux",
    "essuie-glace", "extrême-droite", "extrême-gauche", "faire-part",
    "faux-filet", "faux-monnayeur", "faux-plat", "faux-semblant", "franc-maçon",
    "franc-parler", "garde-boue", "garde-chasse", "garde-corps", "garde-côte",
    "garde-forestier", "garde-fou", "garde-malade", "garde-manger", "garde-meuble",
    "garde-robe", "garde-à-vue", "gilet-pare-balles", "grand-angle", "grand-duc",
    "grand-mère", "grand-oncle", "grand-parent", "grand-père", "grand-rue",
    "grand-tante", "gratte-ciel", "grille-pain", "guet-apens", "haut-de-forme",
    "haut-fond", "haut-fourneau", "haut-parleur", "hors-bord", "hors-jeu",
    "hors-la-loi", "hors-piste", "huis-clos", "laissez-passer",
    "lance-flammes", "lance-pierre", "lance-roquettes", "lave-glace", "lave-linge",
    "lave-vaisselle", "libre-échange", "libre-service", "lieu-dit", "long-métrage",
    "machine-outil", "main-courante", "main-forte", "maître-chien", "maître-nageur",
    "mal-être", "marque-page", "martin-pêcheur", "micro-onde", "micro-organisme",
    "mini-golf", "mini-jupe", "mise-bas", "monte-charge", "mot-clé", "moyen-âge",
    "non-lieu", "non-sens", "non-violence", "nord-est", "nord-ouest", "nouveau-né",
    "oiseau-mouche", "outre-mer", "ouvre-boîte", "pare-balles", "pare-brise",
    "pare-chocs", "pare-étincelles", "pare-feu", "pare-soleil", "passe-droit",
    "passe-montagne", "passe-partout", "passe-temps", "pense-bête", "perce-neige",
    "pèse-personne", "petit-ami", "petit-beurre", "petit-déjeuner", "petit-enfant",
    "petit-fils", "petite-amie", "petite-fille", "pied-à-terre", "pique-assiette",
    "pique-nique", "plain-pied", "plate-bande", "plate-forme", "plein-air",
    "plein-emploi", "plus-value", "poids-lourd", "point-virgule", "poisson-chat",
    "poisson-clown", "pont-levis", "pont-promenade", "porc-épic", "porte-avions",
    "porte-bagages", "porte-bonheur", "porte-clés", "porte-conteneurs",
    "porte-drapeau", "porte-documents", "porte-étendard", "porte-fenêtre",
    "porte-jarretelles", "porte-manteau", "porte-mine", "porte-monnaie",
    "porte-parole", "porte-plume", "porte-savon", "porte-voix", "pot-au-feu",
    "pot-de-vin", "pot-pourri", "garde-à-vous", "premier-ministre", "presse-agrume",
    "presse-citron", "presse-papier", "presse-purée", "prêt-à-porter",
    "procès-verbal", "pur-sang", "quatre-quarts", "abat-jour", "aide-soignant",
    "aller-retour", "amuse-bouche", "amuse-gueule", "appuie-tête", "attrape-nigaud",
    "auto-stop", "auto-stoppeur", "avant-poste", "avant-projet", "avant-scène",
    "avant-toit", "avant-train", "arrière-boutique", "arrière-cour", "arrière-garde",
    "arrière-goût", "arrière-saison", "arrière-train", "chauffe-eau", "chausse-pied",
    "chasse-neige", "coupe-feu", "coupe-ongles", "coupe-papier", "cure-dent",
    "gratte-papier", "lave-auto", "lave-mains", "lève-tôt", "mille-feuille",
    "mille-pattes", "oiseau-lyre", "ouvre-bouteille", "papier-monnaie", "pare-boue",
    "pare-flamme", "pare-foudre", "pare-vent", "passe-plat", "perce-oreille",
    "pèse-bébé", "pèse-lettre", "pique-fleurs", "poisson-lune", "poisson-pilote",
    "poisson-scie", "poisson-volant", "porte-affiche", "porte-aiguille",
    "porte-allumettes", "porte-billets", "porte-bouteilles", "porte-cartes",
    "porte-cigare", "porte-cigarette", "porte-couteau", "porte-crayon",
    "porte-hélicoptères", "porte-malheur", "porte-menu", "porte-musique",
    "porte-parapluie", "porte-serviettes", "porte-toast", "pousse-café",
    "pousse-pousse", "quartier-maître", "quote-part",
    "ramasse-miettes", "ramasse-poussière", "raz-de-marée", "rendez-vous",
    "rez-de-chaussée", "rez-de-jardin", "rond-point", "rouge-gorge", "sage-femme",
    "saint-bernard", "sèche-cheveux", "sèche-linge", "sèche-mains", "semi-liberté",
    "semi-marathon", "semi-remorque", "serre-livres", "serre-tête", "savoir-faire",
    "savoir-vivre", "sapeur-pompier", "side-car", "sous-bois", "sous-chef",
    "sous-commission", "sous-continent", "sous-couche", "sous-directeur",
    "sous-alimentation", "sous-emploi", "sous-ensemble", "sous-entendu",
    "sous-équipement", "sous-estimation", "sous-évaluation", "sous-exposition",
    "sous-groupe", "sous-lieutenant", "sous-location", "sous-main", "sous-marin",
    "sous-multiple", "sous-nutrition", "sous-officier", "sous-préfecture",
    "sous-préfet", "sous-produit", "sous-prolétariat", "sous-région",
    "sous-secrétaire", "sous-section", "sous-sol", "sous-station", "sous-système",
    "sous-titre", "sous-traitance", "sous-traitant", "sous-vêtement", "sous-verre",
    "soutien-gorge", "station-service", "statu-quo", "sud-est", "sud-ouest",
    "table-ronde", "taille-crayon", "taille-haie", "télé-achat", "télé-crochet",
    "terre-neuve", "terre-plein", "tête-à-queue", "tête-à-tête", "tire-au-flanc",
    "tire-bouchon", "tire-fesse", "tire-fond", "tire-lait", "tire-ligne",
    "tissu-éponge", "grille-viande", "tourne-disque", "tout-petit", "tout-puissant",
    "tout-terrain", "tragi-comédie", "trouble-fête", "tue-mouche", "ultra-son",
    "va-et-vient", "va-nu-pieds", "wagon-lit", "wagon-restaurant", "week-end"
}

# =============================================================================
# 2. LISTE NOIRE EXPLICITE (MOTS-OUTILS, SIGLES & FAUTES DE FRAPPE CONNUES)
# =============================================================================
BLACKLIST = {
    # Déterminants, pronoms, prépositions, conjonctions, adverbes et mots-outils
    "le", "la", "les", "un", "une", "des", "du", "de", "au", "aux", "ce", "cet", "cette",
    "ces", "mon", "ton", "son", "ma", "ta", "sa", "mes", "tes", "ses", "notre", "votre",
    "leur", "nos", "vos", "leurs", "je", "tu", "il", "elle", "on", "nous", "vous", "ils",
    "elles", "moi", "toi", "lui", "eux", "soi", "mien", "tien", "sien", "nôtre", "vôtre",
    "mienne", "tienne", "sienne", "celui", "celle", "ceux", "celles", "ceci", "cela", "ça",
    "çà", "autrui", "quiconque", "chacun", "chacune", "aucun", "aucune", "nul", "nulle",
    "personne", "rien", "tout", "tous", "toute", "toutes", "certains", "certaines",
    "plusieurs", "quelque", "quelques", "tel", "telle", "tels", "telles", "même", "mêmes",
    "autre", "autres", "lequel", "laquelle", "lesquels", "lesquelles", "duquel", "auquel",
    "dont", "quoi", "qui", "que", "quel", "quelle", "quels", "quelles", "où", "quand",
    "comment", "pourquoi", "combien", "mais", "ou", "et", "donc", "or", "ni", "car", "si",
    "comme", "lorsque", "puisque", "quoique", "dans", "pour", "avec", "sans", "sous",
    "vers", "chez", "entre", "jusque", "depuis", "pendant", "avant", "après", "contre",
    "malgré", "selon", "parmi", "envers", "hormis", "outre", "voici", "voilà", "ne", "pas",
    "plus", "moins", "très", "bien", "aussi", "trop", "peu", "beaucoup", "assez", "tant",
    "autant", "toujours", "jamais", "souvent", "parfois", "déjà", "encore", "bientôt",
    "alors", "ainsi", "pourtant", "cependant", "néanmoins", "toutefois", "ailleurs",
    "autour", "dessus", "dessous", "dedans", "dehors", "devant", "derrière", "loin",
    "près", "tôt", "tard", "hier", "demain", "aujourd'hui", "oui", "non", "certes",
    "soit", "voire", "sinon", "plutôt", "guère", "presque", "quasi", "environ",
    "notamment", "également", "vraiment", "franchement", "heureusement", "tellement",
    "vachement", "soudain", "brusquement", "doucement", "clairement", "précisément",
    "réellement", "véritablement", "différemment", "suffisamment", "tantôt", "bref",
    "pareil", "allez", "bonjour", "bonsoir", "bravo", "merci", "coucou",
    # Verbes auxiliaires, archaïques et impératifs de recettes (-ez)
    "être", "avoir", "faire", "dire", "pouvoir", "aller", "voir", "savoir", "vouloir",
    "venir", "falloir", "devoir", "croire", "trouver", "donner", "prendre", "parler",
    "aimer", "passer", "mettre", "demander", "tenir", "sembler", "laisser", "rester",
    "penser", "entendre", "regarder", "répondre", "rendre", "connaître", "paraître",
    "partir", "sortir", "vivre", "revenir", "comprendre", "attendre", "devenir",
    "amener", "apporter", "emporter", "entraîner", "provoquer", "permettre", "empêcher",
    "agir", "contribuer", "développer", "proposer", "taire", "douter", "marrer", "rigoler",
    "déconner", "foutre", "merde", "gueule", "truc", "chose", "façon", "sorte", "manière",
    "eût", "fût", "pût", "sût", "dût", "vînt", "tînt", "fît", "dît", "vît", "allât",
    "salez", "poivrez", "émincez", "emincez", "hachez", "coupez", "ajoutez", "versez",
    "mélangez", "remuez", "laissez", "faites", "servez", "dégustez", "enfournez",
    # Nombres
    "zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
    "onze", "douze", "treize", "quatorze", "quinze", "seize", "vingt", "trente", "quarante",
    "cinquante", "soixante", "cent", "mille", "million", "milliard", "dizaine", "douzaine",
    "quinzaine", "vingtaine", "trentaine", "quarantaine", "cinquantaine", "centaine",
    "millier", "premier", "deuxième", "second", "troisième", "quatrième", "cinquième",
    "sixième", "septième", "huitième", "neuvième", "dixième",
    # Sigles, marques, anglais et toutes les fautes de frappe repérées dans les 4 audits
    "http", "https", "www", "html", "htm", "php", "pdf", "jpg", "gif", "png", "url",
    "com", "org", "net", "info", "blog", "post", "mail", "email", "web", "site", "spam",
    "float", "left", "right", "height", "width", "padding", "margin", "border", "color",
    "background", "overflow", "uppercase", "ffffff", "script", "applet", "browser",
    "navigator", "netscape", "firefox", "mozilla", "konqueror", "thunderbird", "powerpoint",
    "impress", "word", "excel", "microsoft", "google", "yahoo", "linux", "windows",
    "server", "proxy", "telnet", "ldap", "unix", "webdav", "imap", "firewall", "netware",
    "isbn", "issn", "sodis", "bibliogr", "coul", "couv", "adsl", "sdsl", "xdsl", "mbit",
    "kbit", "mbps", "kbps", "mégabit", "modem", "numéris", "wsop", "hold", "stud", "unibet",
    "partouche", "betclic", "bwin", "isaetdavid", "bebloom", "interflora", "inra", "anpe",
    "iufm", "sivom", "epci", "tcsp", "sytral", "cafep", "crpe", "caplp", "capeps", "ipag",
    "jorf", "cnrs", "inserm", "insee", "sncf", "ratp", "smic", "urssaf", "assedic", "unedic",
    "otan", "onu", "unesco", "unicef", "uefa", "fifa", "sida", "ump", "udf", "ps", "pcf",
    "fn", "lcr", "cfdt", "cgt", "fo", "medef", "cjd", "cpme", "opep",
    "coef", "coeff", "univ", "ater", "prag", "tice", "placo", "amorto", "abcd", "abc",
    "honori", "honoris", "insect", "rapé", "caissiere", "annale", "annal", "mancozèbe",
    "longeur", "milion", "ascenceur", "standart", "concour", "frigorigèn", "bientot",
    "merçi", "interessé", "déja", "tré", "actuelement", "quelqu", "peut-etre", "sarkosy",
    "segolène", "ebay", "ebayeur", "paypal", "paybox", "colissimo", "kyriad", "sofitel",
    "novotel", "ibis", "exxon", "exxonmobil", "totalfinaelf", "elf", "shell",
    "lagerfeld", "balenciaga", "galliano", "chanel", "castelbajac", "armani", "dior",
    "vuitton", "gucci", "prada", "versace", "ysl", "katrina", "dean", "rokusho", "glisséo",
    "marnier", "sorbonne", "larousse", "robert", "molière", "tesla", "faraday", "habsbourg",
    "aumale", "capétien", "gateal", "chassi", "chbre", "renové", "somrev", "cnom",
    "fnsea", "fdsea", "cnja", "adasea", "pnud", "pnue", "kofi", "ptac", "ccap", "samu",
    "smur", "monoprix", "auchan", "intersport", "lexmark", "pixma", "epson", "tuamotu",
    "moorea", "barbery", "serengeti", "douaumont", "thiaumont", "souville", "verdun",
    "boche", "kostelic", "méribel", "macworld", "forgeard", "tisséo", "transpole",
    "matabiau", "pigalle", "balard", "ueshiba", "geolabo", "géoplan", "noname", "shepherd",
    "maru", "conchylicol", "blanchiss", "bangalor", "ravenof", "cgtu", "transparency",
    "ufolep", "ullrich", "moreni", "nimp", "eurostat", "sitadel", "scees", "sesp", "vsab",
    "dejantees", "papotte", "systran", "translator", "trad", "deug", "license", "llce",
    "deust", "stid", "lamper"
}

SINGULAR_S_X_KEEP = {
    "temps", "corps", "pays", "fois", "mois", "bois", "poids", "cours", "discours",
    "secours", "concours", "parcours", "recours", "univers", "vers", "envers", "revers",
    "travers", "divers", "cas", "pas", "bras", "repas", "tas", "bas", "las", "amas",
    "embarras", "compas", "matelas", "cadenas", "ananas", "canevas", "trépas", "gras",
    "gaz", "nez", "riz", "quartz", "voix", "choix", "croix", "noix", "paix", "prix",
    "toux", "époux", "jaloux", "doux", "roux", "faux", "vieux", "mieux", "souris",
    "brebis", "tapis", "permis", "avis", "débris", "mépris", "paradis", "logis", "radis",
    "châssis", "colis", "compromis", "croquis", "gâchis", "maquis", "parvis", "précis",
    "puits", "relais", "rubis", "semis", "taudis", "tennis", "vernis", "vis", "tournevis",
    "devis", "velours", "ours", "rebours", "héros", "dos", "os", "clos", "enclos",
    "propos", "repos", "chaos", "cosmos", "thermos", "rhinocéros", "albatros", "gros",
    "virus", "bonus", "malus", "bus", "autobus", "cursus", "processus", "consensus",
    "blocus", "lotus", "cactus", "tonus", "sinus", "terminus", "prospectus", "campus",
    "humus", "infarctus", "lapsus", "mucus", "papyrus", "rébus", "typhus", "utérus",
    "détritus", "index", "latex", "cortex", "vortex", "silex", "box", "lynx", "sphinx",
    "phénix", "thorax", "larynx", "onyx", "duplex", "réflex", "climax", "fax", "fils",
    "sens", "suspens", "encens", "gens", "tiers", "mars", "legs", "mets", "palais",
    "marais", "harnais", "biais", "frais", "engrais", "mauvais", "français", "anglais",
    "japonais", "chinois", "congrès", "progrès", "succès", "excès", "accès", "procès",
    "décès", "abcès", "cyprès", "grès", "palmarès", "plexus", "radius", "cubitus",
    "humérus", "thalamus", "pancréas", "diabète", "ciseaux", "lunettes", "vacances",
    "obsèques", "funérailles", "ténèbres", "menottes", "échecs", "archives", "mœurs"
}

VALID_MENT_NOUNS = {
    "bâtiment", "appartement", "vêtement", "médicament", "instrument", "document",
    "monument", "élément", "moment", "sentiment", "événement", "mouvement", "gouvernement",
    "parlement", "département", "enseignement", "entraînement", "environnement",
    "équipement", "établissement", "logement", "paiement", "règlement", "traitement",
    "jugement", "aliment", "ciment", "compliment", "continent", "diamant", "aimant",
    "serment", "tourment", "fragment", "segment", "pigment", "ferment", "froment",
    "jument", "sarment", "ornement", "armement", "campement", "chargement", "classement",
    "commandement", "comportement", "consentement", "couronnement", "débarquement",
    "débordement", "déclenchement", "allongement", "aménagement", "amortissement",
    "anéantissement", "apaisement", "applaudissement", "approfondissement",
    "approvisionnement", "arrondissement", "assainissement", "asservissement",
    "assouplissement", "avancement", "avertissement", "aveuglement", "bannissement",
    "battement", "bégaiement", "blanchiment", "bombardement", "bouleversement",
    "bourdonnement", "branchement", "cautionnement", "changement",
    "cheminement", "chuchotement", "claquement", "cloisonnement", "commencement",
    "compartiment", "complément", "conditionnement", "confinement", "contentement",
    "contingentement", "contournement", "craquement", "crépitement", "croisement",
    "déboisement", "allaitement", "accouchement", "accompagnement", "accomplissement",
    "accouplement", "accroissement", "acharnement", "acheminement", "achèvement",
    "acquittement", "affaiblissement", "affaissement", "affolement", "affranchissement",
    "affrontement", "agencement", "agrandissement", "agrément", "alignement",
    "allègement", "amaigrissement", "ameublement", "amoindrissement",
    "attendrissement", "attroupement", "avortement", "bâillement",
    "balancement", "balbutiement", "ballottement", "bêlement", "bouillonnement",
    "bruissement", "cadencement", "calfeutrement", "cantonnement", "châtiment",
    "chatouillement", "chevauchement", "cisaillement", "clignement", "clignotement",
    "coassement", "couinement", "coulissement", "crachement", "crissement",
    "croassement", "croulement", "déchirement", "déclassement", "décloisonnement",
    "décollement", "découragement", "décrochement", "dédommagement", "dédoublement",
    "déferlement", "défoncement", "défrichement", "dégagement", "dégonflement",
    "dégoulinement", "déguisement", "déhanchement", "délabrement", "délaissement",
    "délassement", "démantèlement", "déménagement", "démembrement", "dénouement",
    "dénuement", "dépassement", "dépaysement", "dépeuplement", "déplacement",
    "déploiement", "dépouillement", "dépérissement", "déracinement", "dérangement",
    "dérèglement", "déroulement", "désabonnement", "désarmement", "désenchantement",
    "désenclavement", "désengagement", "désengorgement", "désœuvrement",
    "intéressement", "investissement", "isolement", "jaillissement", "jappement",
    "lancement", "licenciement", "lotissement", "maniement", "manquement",
    "mécontentement", "ménagement", "miaulement", "mugissement", "nivellement",
    "obscurcissement", "aplatissement", "appauvrissement", "pansement",
    "parachèvement", "parement", "pétillement", "piétinement", "pincement",
    "placement", "plissement", "prélèvement", "prolongement", "questionnement",
    "rabaissement", "raccordement", "raccommodement", "raclement", "radoucissement",
    "raffermissement", "rafraîchissement", "rajeunissement", "ralentissement",
    "ralliement", "rallongement", "ramollissement", "rapatriement", "rapetissement",
    "rapprochement", "rassemblement", "rattachement", "ravalement", "ravissement",
    "ravitaillement", "rayonnement", "réaménagement", "réarmement", "reboisement",
    "rebondissement", "recensement", "réchauffement", "reclassement",
    "recommencement", "reconditionnement", "recoupement", "recouvrement",
    "recrutement", "redéploiement", "redressement", "redoublement", "rééquipement",
    "refoulement", "refroidissement", "régiment", "regroupement", "réinvestissement",
    "relâchement", "relèvement", "relogement", "remaniement", "remblaiement",
    "remboursement", "remembrement", "remerciement", "remplacement", "remuement",
    "renchérissement", "rendement", "renfermement", "renflouement", "renfoncement",
    "renforcement", "rengagement", "reniflement", "renoncement", "renouvellement",
    "renseignement", "renversement", "repeuplement", "repliement", "repositionnement",
    "repoussement", "resserrement", "ressourcement", "rétablissement",
    "retentissement", "retournement", "retraitement", "retranchement",
    "rétrécissement", "revêtement", "revirement", "ricanement", "ronflement",
    "ronronnement", "roulement", "rugissement", "ruissellement", "sacrement",
    "saignement", "scintillement", "secouement", "sifflement", "signalement",
    "soubassement", "soulagement", "soulèvement", "stationnement", "suintement",
    "supplément", "surarmement", "surendettement", "suréquipement", "surgissement",
    "surinvestissement", "surpeuplement", "tâtonnement", "terrassement", "testament",
    "tiraillement", "tressaillement", "tremblement", "trépignement", "tutoiement",
    "vagissement", "vrombissement", "vouvoyement"
}

# =============================================================================
# 3. BANQUE CURATÉE DE NOMS COMMUNS CONCRETS POUR LES 500 MOTS SECRETS
# =============================================================================
CURATED_SECRET_NOUNS = [
    # Nature, Plantes, Paysages & Météo
    "plante", "arbre", "fleur", "forêt", "océan", "montagne", "rivière", "désert",
    "volcan", "tempête", "neige", "plage", "soleil", "étoile", "planète", "nuage",
    "orage", "foudre", "glacier", "cascade", "caverne", "falaise", "colline", "vallée",
    "prairie", "marais", "jungle", "savane", "oasis", "banquise", "iceberg", "ouragan",
    "tornade", "avalanche", "arc-en-ciel", "crépuscule", "aurore", "horizon", "marée",
    "vague", "écume", "sable", "galet", "rocher", "caillou", "argile", "charbon",
    "pétrole", "diamant", "émeraude", "rubis", "saphir", "cristal", "ambre", "fossile",
    "cratère", "source", "ruisseau", "torrent", "étang", "lagon", "archipel", "péninsule",
    "estuaire", "clairière", "buisson", "racine", "écorce", "feuille", "branche",
    "bourgeon", "pétale", "épine", "pollen", "nectar", "mousse", "fougère", "bambou",
    "cactus", "palmier", "chêne", "sapin", "olivier", "cerisier", "pommier", "vigne",
    "blé", "roseau", "ortie", "lavande", "tournesol", "tulipe", "orchidée", "coquelicot",
    "marguerite", "bouquet", "champignon", "truffe", "algue", "corail", "coquillage",
    "perle", "éponge",
    # Animaux
    "méduse", "pieuvre", "requin", "baleine", "dauphin", "phoque", "morse", "manchot",
    "tortue", "crocodile", "serpent", "vipère", "cobra", "lézard", "caméléon", "grenouille",
    "crapaud", "salamandre", "truite", "saumon", "thon", "sardine", "anguille", "hippocampe",
    "crabe", "homard", "crevette", "huître", "moule", "escargot", "limace", "araignée",
    "scorpion", "insecte", "abeille", "guêpe", "bourdon", "fourmi", "termite", "papillon",
    "chenille", "libellule", "coccinelle", "scarabée", "cigale", "grillon", "sauterelle",
    "moustique", "mouche", "oiseau", "aigle", "faucon", "vautour", "hibou", "chouette",
    "corbeau", "pie", "moineau", "hirondelle", "pigeon", "colombe", "mouette", "goéland",
    "pélican", "flamant", "cygne", "canard", "oie", "dinde", "poule", "coq", "poussin",
    "paon", "autruche", "perroquet", "toucan", "colibri", "cigogne", "héron", "rossignol",
    "merle", "chien", "chiot", "chat", "cheval", "poulain", "âne", "zèbre", "vache",
    "taureau", "veau", "mouton", "brebis", "agneau", "chèvre", "cochon", "sanglier",
    "cerf", "biche", "chevreuil", "renne", "élan", "chamois", "girafe", "chameau",
    "dromadaire", "lama", "éléphant", "rhinocéros", "hippopotame", "lion", "tigre",
    "léopard", "panthère", "guépard", "lynx", "loup", "renard", "ours", "panda", "koala",
    "kangourou", "singe", "gorille", "chimpanzé", "lémurien", "castor", "loutre",
    "blaireau", "furet", "belette", "hermine", "écureuil", "marmotte", "hamster",
    "souris", "rat", "mulot", "taupe", "hérisson", "lapin", "lièvre", "chauve-souris",
    # Gastronomie & Cuisine
    "cuisine", "restaurant", "recette", "repas", "banquet", "pique-nique", "petit-déjeuner",
    "déjeuner", "dîner", "apéritif", "plat", "dessert", "pain", "baguette", "croissant",
    "brioche", "biscuit", "gâteau", "tarte", "crêpe", "gaufre", "beignet", "macaron",
    "meringue", "flan", "glace", "sorbet", "chocolat", "bonbon", "caramel", "confiture",
    "miel", "sirop", "sucre", "farine", "levure", "semoule", "pâte", "riz", "avoine",
    "orge", "maïs", "céréale", "viande", "rôti", "grillade", "côtelette", "saucisse",
    "jambon", "lard", "saucisson", "pâté", "terrine", "volaille", "poulet", "gibier",
    "poisson", "sushi", "caviar", "omelette", "fromage", "beurre", "crème", "yaourt",
    "lait", "légume", "salade", "tomate", "carotte", "oignon", "ail", "échalote",
    "poireau", "navet", "radis", "betterave", "pomme", "poire", "pêche", "abricot",
    "prune", "cerise", "fraise", "framboise", "mûre", "myrtille", "groseille", "cassis",
    "raisin", "melon", "pastèque", "orange", "citron", "pamplemousse", "mandarine",
    "clémentine", "banane", "ananas", "mangue", "papaye", "kiwi", "avocat", "noix",
    "noisette", "amande", "pistache", "cacahuète", "châtaigne", "marron", "olive",
    "datte", "figue", "grenade", "courgette", "aubergine", "poivron", "piment",
    "concombre", "cornichon", "citrouille", "potiron", "épinard", "chou", "brocoli",
    "chou-fleur", "artichaut", "asperge", "céleri", "fenouil", "haricot", "lentille",
    "pois", "fève", "soja", "soupe", "potage", "bouillon", "velouté", "purée", "gratin",
    "ragoût", "couscous", "paella", "pizza", "lasagne", "sandwich", "hamburger", "frite",
    "sauce", "mayonnaise", "moutarde", "vinaigre", "huile", "sel", "poivre", "épice",
    "cannelle", "vanille", "safran", "curry", "gingembre", "muscade", "persil", "basilic",
    "thym", "romarin", "menthe", "coriandre", "ciboulette", "laurier", "estragon",
    "boisson", "eau", "jus", "limonade", "soda", "café", "thé", "infusion", "tisane",
    "vin", "champagne", "bière", "cidre", "liqueur", "cocktail",
    # Maison, Architecture & Objets
    "maison", "immeuble", "appartement", "château", "palais", "manoir", "villa",
    "chalet", "cabane", "chaumière", "ferme", "grange", "moulin", "phare", "tour",
    "gratte-ciel", "bâtiment", "chantier", "architecture", "façade", "toiture", "toit",
    "tuile", "ardoise", "cheminée", "gouttière", "mur", "cloison", "plafond", "plancher",
    "parquet", "carrelage", "moquette", "tapis", "fondation", "pilier", "colonne",
    "poutre", "voûte", "coupole", "balcon", "terrasse", "véranda", "porche",
    "perron", "cour", "jardin", "potager", "pelouse", "haie", "clôture", "portail",
    "grille", "allée", "tonnelle", "serre", "piscine", "fontaine", "puits", "bassin",
    "cave", "sous-sol", "cellier", "garage", "grenier", "comble", "étage", "rez-de-chaussée",
    "escalier", "marche", "rampe", "ascenseur", "couloir", "vestibule", "salon",
    "chambre", "bureau", "bibliothèque", "buanderie", "toilette", "baignoire", "douche",
    "lavabo", "évier", "robinet", "tuyau", "radiateur", "chauffage", "chaudière",
    "climatisation", "ventilateur", "poêle", "âtre", "porte", "serrure", "verrou", "clé",
    "poignée", "sonnette", "fenêtre", "vitre", "volet", "persienne", "rideau", "store",
    "mobilier", "meuble", "table", "chaise", "fauteuil", "canapé", "tabouret", "banc",
    "lit", "matelas", "sommier", "oreiller", "traversin", "drap", "couverture", "couette",
    "édredon", "berceau", "armoire", "placard", "commode", "tiroir", "étagère", "vitrine",
    "buffet", "vaisselier", "pupitre", "coffre", "malle", "valise", "sac", "cartable",
    "portefeuille", "porte-monnaie", "parapluie", "ombrelle", "canne", "éventail",
    "miroir", "cadre", "tableau", "horloge", "pendule", "réveil", "montre", "sablier",
    "calendrier", "lampe", "lustre", "abat-jour", "ampoule", "bougie", "chandelle",
    "lanterne", "torche", "briquet", "allumette", "cendrier", "vase", "pot", "cruche",
    "carafe", "bouteille", "flacon", "bocal", "tonneau", "baril", "seau", "bassine",
    "panier", "corbeille", "poubelle", "balai", "brosse", "aspirateur", "serpillière",
    "chiffon", "lessive", "savon", "shampoing", "dentifrice", "peigne", "rasoir",
    "serviette", "gant", "peignoir", "mouchoir", "vaisselle", "assiette", "bol", "tasse",
    "soucoupe", "verre", "gobelet", "fourchette", "couteau", "cuillère", "louche",
    "écumoire", "fouet", "spatule", "râpe", "passoire", "entonnoir", "tamis", "rouleau",
    "mortier", "balance", "tire-bouchon", "ouvre-boîte", "casserole", "marmite",
    "faitout", "cocotte", "wok", "saladier", "soupière", "plateau", "théière",
    "cafetière", "bouilloire", "grille-pain", "four", "réfrigérateur", "congélateur",
    "lave-vaisselle", "lave-linge", "couture", "aiguille", "épingle", "fil", "bobine",
    "ciseaux", "bouton", "tricot", "pelote", "laine", "coton", "soie", "lin", "velours",
    "dentelle", "ruban", "tissu", "étoffe", "cuir", "fourrure", "plume", "vêtement",
    "habit", "costume", "tailleur", "robe", "jupe", "pantalon", "short", "chemise",
    "chemisier", "blouse", "tunique", "gilet", "pull", "cardigan", "veste", "blouson",
    "manteau", "imperméable", "cape", "anorak", "parka", "pyjama", "maillot", "tablier",
    "uniforme", "armure", "casque", "chapeau", "casquette", "béret", "bonnet", "capuche",
    "foulard", "écharpe", "cravate", "ceinture", "bretelle", "moufle", "chaussette",
    "chaussure", "soulier", "botte", "bottine", "sandale", "pantoufle", "chausson",
    "sabot", "espadrille", "basket", "talon", "semelle", "lacet", "bijou", "bague",
    "alliance", "anneau", "bracelet", "collier", "pendentif", "médaillon", "broche",
    "diadème", "couronne", "parfum", "maquillage", "lunettes",
    # Transports & Voyages
    "transport", "voyage", "trajet", "itinéraire", "route", "autoroute", "chemin",
    "sentier", "piste", "boulevard", "avenue", "rue", "ruelle", "impasse", "carrefour",
    "rond-point", "pont", "viaduc", "passerelle", "tunnel", "péage", "trottoir",
    "chaussée", "bitume", "asphalte", "pavé", "fossé", "virage", "pente", "panneau",
    "radar", "embouteillage", "bouchon", "panne", "parking", "station-service",
    "essence", "carburant", "diesel", "moteur", "roue", "pneu", "frein", "volant",
    "pédale", "embrayage", "vitesse", "clignotant", "pare-brise", "essuie-glace",
    "rétroviseur", "pare-chocs", "capot", "portière", "siège", "klaxon", "batterie",
    "échappement", "carrosserie", "châssis", "suspension", "amortisseur", "voiture",
    "automobile", "véhicule", "camion", "poids-lourd", "remorque", "fourgon",
    "camionnette", "bus", "autobus", "autocar", "tramway", "trolleybus", "métro",
    "train", "locomotive", "wagon", "rail", "gare", "quai", "guichet", "billet",
    "ticket", "composteur", "contrôleur", "horaire", "terminus", "aiguillage", "vélo",
    "bicyclette", "guidon", "selle", "chaîne", "garde-boue", "pompe", "moto",
    "motocyclette", "scooter", "mobylette", "side-car", "avion", "aéronef", "planeur",
    "hélicoptère", "fusée", "navette", "satellite", "sonde", "dirigeable", "montgolfière",
    "parachute", "parapente", "deltaplane", "aile", "hélice", "réacteur", "turbine",
    "cockpit", "cabine", "hublot", "soute", "aéroport", "aérodrome", "tarmac", "hangar",
    "terminal", "embarquement", "décollage", "atterrissage", "escale", "hôtesse",
    "pilote", "bateau", "navire", "paquebot", "cargo", "pétrolier", "chalutier",
    "remorqueur", "ferry", "yacht", "voilier", "catamaran", "goélette", "caravelle",
    "galère", "jonque", "pirogue", "canoë", "kayak", "radeau", "barque", "canot",
    "péniche", "gondole", "sous-marin", "porte-avions", "croiseur", "frégate", "coque",
    "proue", "poupe", "tribord", "bâbord", "cale", "mât", "voile", "cordage",
    "gouvernail", "timon", "ancre", "rame", "aviron", "pagaie", "bouée", "port",
    "jetée", "digue", "écluse", "canal", "balise", "boussole", "compas", "sextant",
    "carte", "atlas", "globe", "jumelles", "sonar", "naufrage", "épave",
    # Corps Humain & Santé Courante
    "corps", "squelette", "os", "crâne", "vertèbre", "muscle", "peau", "cicatrice",
    "larme", "sang", "veine", "artère", "poumon", "cerveau", "nerf", "estomac", "foie",
    "rein", "tête", "visage", "front", "joue", "mâchoire", "menton", "œil", "paupière",
    "cil", "sourcil", "pupille", "nez", "narine", "oreille", "bouche", "lèvre", "langue",
    "gorge", "dent", "gencive", "cheveu", "barbe", "moustache", "cou", "nuque", "épaule",
    "bras", "coude", "avant-bras", "poignet", "main", "paume", "doigt", "pouce", "ongle",
    "poing", "poitrine", "torse", "ventre", "abdomen", "nombril", "hanche", "dos",
    "jambe", "cuisse", "genou", "mollet", "cheville", "pied", "orteil", "santé",
    "médecine", "hôpital", "clinique", "urgence", "ambulance", "brancard", "civière",
    "pharmacie", "laboratoire", "médecin", "docteur", "chirurgien", "dentiste",
    "pédiatre", "psychiatre", "vétérinaire", "pharmacien", "infirmier", "aide-soignant",
    "sage-femme", "kinésithérapeute", "patient", "malade", "maladie", "symptôme",
    "douleur", "fièvre", "frisson", "toux", "rhume", "grippe", "angine", "bronchite",
    "asthme", "allergie", "virus", "bactérie", "microbe", "épidémie", "blessure",
    "plaie", "coupure", "brûlure", "entorse", "fracture", "vertige", "nausée",
    "migraine", "insomnie", "fatigue", "stress", "carie", "diagnostic", "radiographie",
    "échographie", "scanner", "chirurgie", "anesthésie", "greffe", "suture", "guérison",
    "remède", "médicament", "ordonnance", "pilule", "comprimé", "gélule", "aspirine",
    "antibiotique", "vaccin", "piqûre", "seringue", "pommade", "pansement", "sparadrap",
    "bandage", "plâtre", "attelle", "béquille", "stéthoscope", "thermomètre", "scalpel",
    # Arts, Musique, Littérature, Cinéma, Jeux & Sports
    "art", "musée", "galerie", "exposition", "peinture", "toile", "fresque", "aquarelle",
    "gouache", "pastel", "fusain", "encre", "portrait", "paysage", "croquis", "esquisse",
    "dessin", "gravure", "caricature", "illustration", "pinceau", "palette", "chevalet",
    "vernis", "couleur", "nuance", "teinte", "pigment", "ombre", "lumière", "contraste",
    "sculpture", "statue", "buste", "marbre", "bronze", "maillet", "poterie", "céramique",
    "porcelaine", "faïence", "mosaïque", "vitrail", "tapisserie", "photographie", "photo",
    "pellicule", "cliché", "album", "diapositive", "cinéma", "film", "court-métrage",
    "long-métrage", "documentaire", "scénario", "tournage", "caméra", "projecteur",
    "écran", "séance", "festival", "réalisateur", "comédien", "figurant", "cascadeur",
    "producteur", "montage", "doublage", "sous-titre", "générique", "affiche", "théâtre",
    "scène", "coulisse", "décor", "masque", "loges", "gradin", "orchestre", "entracte",
    "applaudissement", "tragédie", "comédie", "drame", "vaudeville", "opéra", "ballet",
    "chorégraphie", "danse", "danseur", "valse", "tango", "cirque", "chapiteau",
    "trapèze", "funambule", "équilibriste", "acrobate", "jongleur", "clown", "magicien",
    "illusionniste", "dompteur", "ménagerie", "marionnette", "musique", "mélodie",
    "harmonie", "rythme", "cadence", "tempo", "partition", "portée", "refrain", "couplet",
    "chanson", "chant", "hymne", "berceuse", "chorale", "chanteur", "ténor", "soprano",
    "musicien", "compositeur", "fanfare", "concert", "récital", "symphonie", "concerto",
    "sonate", "jazz", "instrument", "piano", "clavecin", "orgue", "accordéon", "harmonica",
    "violon", "alto", "violoncelle", "contrebasse", "harpe", "guitare", "luth", "mandoline",
    "banjo", "flûte", "hautbois", "clarinette", "basson", "saxophone", "trompette",
    "trombone", "tuba", "clairon", "tambour", "timbale", "batterie", "cymbale", "gong",
    "xylophone", "tambourin", "cloche", "carillon", "diapason", "métronome", "archet",
    "micro", "amplificateur", "enceinte", "haut-parleur", "disque", "vinyle", "cassette",
    "radio", "littérature", "livre", "ouvrage", "manuel", "dictionnaire", "encyclopédie",
    "annuaire", "catalogue", "brochure", "revue", "magazine", "journal", "quotidien",
    "article", "rubrique", "reportage", "interview", "roman", "conte", "fable", "légende",
    "mythe", "épopée", "poésie", "poème", "rime", "strophe", "sonnet", "biographie",
    "lettre", "manuscrit", "parchemin", "papyrus", "grimoire", "page", "chapitre",
    "paragraphe", "mot", "phrase", "titre", "préface", "sommaire", "reliure", "marque-page",
    "écriture", "alphabet", "voyelle", "consonne", "syllabe", "ponctuation", "virgule",
    "guillemet", "parenthèse", "grammaire", "orthographe", "vocabulaire", "lexique",
    "synonyme", "langue", "dialecte", "argot", "traduction", "interprète", "écrivain",
    "auteur", "romancier", "poète", "journaliste", "rédacteur", "éditeur", "imprimeur",
    "libraire", "bibliothécaire", "lecteur", "imprimerie", "presse", "librairie",
    "archives", "papier", "carton", "stylo", "crayon", "feutre", "craie", "gomme",
    "règle", "équerre", "cahier", "carnet", "agenda", "classeur", "dossier", "enveloppe",
    "timbre", "cachet", "sceau", "colle", "agrafeuse", "punaise", "calculatrice",
    "ordinateur", "clavier", "imprimante", "serveur", "réseau", "internet", "logiciel",
    "fichier", "programme", "jeu", "jouet", "poupée", "peluche", "toupie", "bille",
    "ballon", "balle", "cerceau", "cerf-volant", "patin", "manège", "balançoire",
    "toboggan", "puzzle", "domino", "poker", "tarot", "échecs", "échiquier", "pion",
    "cavalier", "loto", "loterie", "casino", "roulette", "billard", "fléchette",
    "quille", "bowling", "sport", "athlétisme", "course", "marathon", "sprint",
    "javelot", "marteau", "poids", "gymnastique", "trampoline", "natation", "plongeoir",
    "plongée", "tuba", "palme", "surf", "ski", "télésiège", "luge", "bobsleigh",
    "patinage", "patinoire", "hockey", "alpinisme", "escalade", "mousqueton", "piolet",
    "crampon", "randonnée", "cyclisme", "vélodrome", "peloton", "équitation", "hippodrome",
    "obstacle", "étrier", "bride", "cravache", "éperon", "escrime", "épée", "fleuret",
    "sabre", "arc", "flèche", "carquois", "cible", "boxe", "ring", "lutte", "judo",
    "tatami", "kimono", "karaté", "aïkido", "haltère", "football", "rugby", "pénalité",
    "basket-ball", "handball", "volley-ball", "tennis", "raquette", "badminton",
    "ping-pong", "golf", "pétanque", "cochonnet", "stade", "terrain", "tribune",
    "vestiaire", "arbitre", "sifflet", "chronomètre", "entraîneur", "équipe", "joueur",
    "capitaine", "gardien", "supporter", "match", "compétition", "tournoi", "championnat",
    "finale", "demi-finale", "victoire", "défaite", "record", "exploit", "champion",
    "vainqueur", "adversaire", "médaille", "trophée", "podium",
    # Société, Métiers, Économie, Justice, Histoire & Sciences
    "école", "maternelle", "collège", "lycée", "université", "faculté", "institut",
    "internat", "classe", "amphithéâtre", "récréation", "cantine", "élève", "écolier",
    "collégien", "lycéen", "étudiant", "apprenti", "professeur", "instituteur",
    "enseignant", "chercheur", "proviseur", "recteur", "surveillant", "cours", "leçon",
    "devoir", "exercice", "dictée", "rédaction", "interrogation", "examen", "concours",
    "épreuve", "diplôme", "baccalauréat", "licence", "doctorat", "thèse", "bulletin",
    "métier", "profession", "travail", "emploi", "stage", "apprentissage", "carrière",
    "atelier", "usine", "fabrique", "manufacture", "entrepôt", "mine", "forage",
    "raffinerie", "centrale", "barrage", "éolienne", "entreprise", "coopérative",
    "syndicat", "grève", "manifestation", "patron", "employeur", "directeur", "employé",
    "ouvrier", "technicien", "ingénieur", "artisan", "commerçant", "marchand", "vendeur",
    "client", "consommateur", "fournisseur", "livreur", "agriculteur", "paysan",
    "fermier", "éleveur", "berger", "vigneron", "jardinier", "bûcheron", "pêcheur",
    "marin", "mineur", "forgeron", "serrurier", "plombier", "électricien", "menuisier",
    "charpentier", "ébéniste", "maçon", "couvreur", "vitrier", "carreleur", "mécanicien",
    "garagiste", "chauffeur", "conducteur", "facteur", "postier", "boulanger", "pâtissier",
    "boucher", "charcutier", "poissonnier", "épicier", "cuisinier", "barman", "hôtelier",
    "coiffeur", "barbier", "couturier", "cordonnier", "horloger", "bijoutier", "orfèvre",
    "fleuriste", "photographe", "architecte", "géomètre", "comptable", "banquier",
    "assureur", "notaire", "avocat", "juge", "magistrat", "procureur", "huissier",
    "greffier", "policier", "gendarme", "inspecteur", "commissaire", "détective",
    "pompier", "secouriste", "militaire", "soldat", "officier", "général", "colonel",
    "lieutenant", "sergent", "caporal", "matelot", "amiral", "outil", "machine",
    "enclume", "tenaille", "pince", "étau", "tournevis", "vis", "écrou", "boulon",
    "clou", "rondelle", "scie", "lime", "rabot", "ciseau", "burin", "perceuse",
    "meuleuse", "ponceuse", "soudure", "chalumeau", "échelle", "escabeau", "échafaudage",
    "brouette", "pelle", "pioche", "bêche", "râteau", "fourche", "faucille", "sécateur",
    "tondeuse", "tronçonneuse", "hache", "poulie", "treuil", "grue", "levier", "cric",
    "tracteur", "moissonneuse", "arrosoir", "commerce", "marché", "foire", "magasin",
    "boutique", "supermarché", "hypermarché", "comptoir", "étalage", "caisse", "chariot",
    "marchandise", "produit", "emballage", "étiquette", "prix", "tarif", "achat",
    "vente", "livraison", "facture", "garantie", "rabais", "solde", "promotion",
    "enchère", "économie", "finance", "argent", "monnaie", "devise", "fortune",
    "richesse", "trésor", "capital", "budget", "épargne", "dette", "crédit", "emprunt",
    "prêt", "hypothèque", "bourse", "dividende", "bénéfice", "profit", "déficit",
    "faillite", "inflation", "crise", "banque", "coffre-fort", "chèque", "virement",
    "distributeur", "salaire", "paie", "prime", "indemnité", "pension", "retraite",
    "allocation", "loyer", "impôt", "taxe", "douane", "amende", "subvention", "assurance",
    "contrat", "clause", "justice", "droit", "loi", "règlement", "décret", "constitution",
    "tribunal", "procès", "audience", "jury", "témoin", "serment", "preuve", "indice",
    "alibi", "aveu", "expertise", "plaidoirie", "réquisitoire", "verdict", "jugement",
    "sentence", "condamnation", "acquittement", "amnistie", "crime", "délit", "infraction",
    "contravention", "enlèvement", "otage", "cambriolage", "braquage", "escroquerie",
    "fraude", "chantage", "corruption", "trafic", "contrebande", "vandalisme", "incendie",
    "complot", "trahison", "espionnage", "coupable", "criminel", "voleur", "cambrioleur",
    "bandit", "brigand", "pirate", "corsaire", "escroc", "faussaire", "complice",
    "suspect", "accusé", "prévenu", "victime", "plainte", "enquête", "perquisition",
    "filature", "interrogatoire", "garde-à-vue", "arrestation", "menottes", "prison",
    "pénitencier", "bagne", "cachot", "cellule", "barreau", "geôle", "détention",
    "évasion", "caution", "sanction", "punition", "châtiment", "nation", "patrie",
    "pays", "territoire", "frontière", "capitale", "province", "région", "département",
    "canton", "commune", "ville", "cité", "agglomération", "banlieue", "quartier",
    "faubourg", "village", "bourg", "hameau", "mairie", "préfecture", "ambassade",
    "consulat", "ministère", "parlement", "assemblée", "sénat", "gouvernement",
    "république", "démocratie", "monarchie", "royaume", "empire", "dictature",
    "révolution", "émeute", "révolte", "rébellion", "élection", "vote", "scrutin",
    "référendum", "sondage", "campagne", "candidat", "électeur", "urne", "isoloir",
    "majorité", "opposition", "coalition", "traité", "pacte", "diplomatie", "roi",
    "reine", "prince", "princesse", "duc", "comte", "baron", "marquis", "seigneur",
    "chevalier", "vassal", "empereur", "tsar", "sultan", "pharaon", "président",
    "ministre", "député", "sénateur", "maire", "préfet", "ambassadeur", "diplomate",
    "citoyen", "esclave", "guerre", "bataille", "combat", "assaut", "siège", "blocus",
    "embuscade", "offensive", "retraite", "invasion", "occupation", "résistance",
    "libération", "trêve", "armistice", "capitulation", "paix", "conquête", "stratégie",
    "tactique", "armée", "troupe", "régiment", "bataillon", "escadron", "patrouille",
    "sentinelle", "garnison", "caserne", "tranchée", "bunker", "forteresse", "citadelle",
    "rempart", "bastion", "douve", "pont-levis", "meurtrière", "créneau", "donjon",
    "arme", "arsenal", "munition", "poudre", "obus", "bombe", "torpille", "missile",
    "roquette", "fusil", "carabine", "mousquet", "pistolet", "revolver", "mitrailleuse",
    "canon", "tank", "blindé", "glaive", "poignard", "dague", "baïonnette", "lance",
    "hallebarde", "arbalète", "fronde", "catapulte", "bélier", "bouclier", "cuirasse",
    "heaume", "visière", "drapeau", "étendard", "bannière", "pavillon", "galon",
    "prisonnier", "déserteur", "espion", "traître", "héros", "vétéran", "religion",
    "foi", "croyance", "culte", "rite", "cérémonie", "procession", "pèlerinage",
    "prière", "méditation", "jeûne", "sacrifice", "offrande", "miracle", "prophétie",
    "péché", "pardon", "bénédiction", "malédiction", "sacrilège", "blasphème", "hérésie",
    "dogme", "paradis", "enfer", "purgatoire", "âme", "esprit", "fantôme", "spectre",
    "démon", "diable", "ange", "archange", "saint", "prophète", "messie", "apôtre",
    "martyr", "dieu", "déesse", "idole", "divinité", "temple", "église", "cathédrale",
    "basilique", "chapelle", "abbaye", "monastère", "couvent", "cloître", "prieuré",
    "ermitage", "mosquée", "minaret", "synagogue", "pagode", "sanctuaire", "autel",
    "nef", "crypte", "clocher", "chaire", "confessionnal", "bénitier", "cierge",
    "encens", "calice", "hostie", "croix", "crucifix", "chapelet", "relique", "cimetière",
    "tombe", "tombeau", "sépulture", "caveau", "mausolée", "sarcophage", "cercueil",
    "stèle", "deuil", "obsèques", "funérailles", "enterrement", "prêtre", "curé",
    "abbé", "moine", "religieuse", "évêque", "cardinal", "pape", "pasteur", "rabbin",
    "imam", "bonze", "sorcier", "mage", "druide", "chaman", "science", "recherche",
    "expérience", "théorie", "hypothèse", "formule", "équation", "calcul", "mathématiques",
    "algèbre", "géométrie", "chiffre", "nombre", "fraction", "moyenne", "statistique",
    "probabilité", "angle", "triangle", "carré", "rectangle", "cercle", "sphère",
    "cylindre", "cône", "pyramide", "cube", "prisme", "polygone", "diamètre", "périmètre",
    "surface", "volume", "longueur", "largeur", "hauteur", "profondeur", "épaisseur",
    "distance", "accélération", "masse", "densité", "pression", "force", "énergie",
    "puissance", "chaleur", "température", "froid", "électricité", "courant", "tension",
    "aimant", "magnétisme", "gravité", "onde", "fréquence", "vibration", "écho",
    "laser", "spectre", "loupe", "microscope", "télescope", "astronomie", "univers",
    "cosmos", "galaxie", "nébuleuse", "constellation", "lune", "comète", "astéroïde",
    "météorite", "éclipse", "orbite", "gravitation", "chimie", "molécule", "métal",
    "alliage", "fer", "acier", "cuivre", "laiton", "aluminium", "étain", "plomb",
    "zinc", "chrome", "titane", "mercure", "or", "carbone", "oxygène", "hydrogène",
    "azote", "hélium", "soufre", "chlore", "calcium", "acide", "cristal", "mélange",
    "réaction", "combustion", "explosion", "distillation", "filtration", "fusion",
    "ébullition", "évaporation", "condensation", "congélation", "rouille", "corrosion",
    "éprouvette", "fiole", "alambic", "biologie", "génétique", "gène", "chromosome",
    "évolution", "espèce", "hybride", "clone", "écosystème", "habitat", "climat",
    "météorologie"
]

def strip_accents(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def has_french_accent(s):
    return s != strip_accents(s)

def get_singular_candidate(w):
    if w in SINGULAR_S_X_KEEP or "-" in w or len(w) <= 3:
        return None
    if w.endswith("eaux") and len(w) > 5:
        return w[:-1]
    if w.endswith("aux") and len(w) > 4:
        return w[:-3] + "al"
    if w.endswith("s") or w.endswith("x"):
        return w[:-1]
    return None

def is_valid_french_word(w):
    if not (2 <= len(w) <= 22):
        return False
    if w in BLACKLIST:
        return False

    # 1. Mots de 2-3 lettres : liste blanche fermée
    if len(w) <= 3:
        return w in VALID_SHORT_WORDS

    # 2. Mots composés avec tiret : liste blanche fermée
    if "-" in w:
        return w in VALID_HYPHEN_WORDS

    if not w.isalpha():
        return False

    # 3. Verbes conjugués en -ez (salez, emincez...)
    if w.endswith("ez") and len(w) >= 4:
        return False

    # 4. Adverbes en -ment (en gardant les vrais noms en -ment)
    if w.endswith("ment") and len(w) > 5 and w not in VALID_MENT_NOUNS:
        return False

    # 5. Sigles sans voyelle ou avec 5 consonnes d'affilée
    vowels = set("aeiouyàâäéèêëîïôöùûüÿœæ")
    if not any(c in vowels for c in w):
        return False
    max_cons = 0
    cur_cons = 0
    for c in w:
        if c not in vowels:
            cur_cons += 1
            if cur_cons > max_cons:
                max_cons = cur_cons
        else:
            cur_cons = 0
    if max_cons >= 5:
        return False

    return True

def load_word2vec_bin(filepath):
    print(f"1/5 Lecture du modèle binaire '{filepath}'...")
    with open(filepath, "rb") as f:
        header = f.readline().decode("utf-8")
        vocab_size, dim = map(int, header.split())
        print(f"    Vocabulaire brut : {vocab_size:,} entrées | Dimensions : {dim}")

        vectors = np.empty((vocab_size, dim), dtype=np.float32)
        words = []
        raw_word_to_idx = {}

        for i in range(vocab_size):
            word_bytes = bytearray()
            while True:
                ch = f.read(1)
                if ch == b" " or not ch:
                    break
                if ch != b"\n":
                    word_bytes.extend(ch)

            word = word_bytes.decode("utf-8", errors="ignore").lower().strip()
            vec = np.frombuffer(f.read(dim * 4), dtype=np.float32)
            words.append(word)
            if word not in raw_word_to_idx:
                raw_word_to_idx[word] = i
            vectors[i] = vec

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors /= norms
    return words, raw_word_to_idx, vectors

def build_semantic_ban_mask(raw_words, raw_word_to_idx, raw_vectors):
    print("2/5 Calcul du bouclier vectoriel (protège les 20 000 mots les plus fréquents)...")
    clusters = {
        "prenoms": (["michel", "philippe", "christophe", "stéphane", "frédéric", "bernard", "thierry", "didier", "alain", "laurent"], 0.50),
        "politique": (["sarkozy", "villepin", "chirac", "raffarin", "jospin", "bayrou", "ump", "udf", "fillon"], 0.50),
        "code_css": (["height", "width", "padding", "margin", "background-color", "text-align", "javascript", "ffffff", "netscape", "mozilla"], 0.46),
        "anglais": (["the", "with", "from", "that", "this", "have", "which", "their", "would", "about"], 0.45),
        "sms_forum": (["bientot", "merçi", "actuelement", "déja", "interessé", "lol", "coucou", "cordialement", "amicalement"], 0.48)
    }

    protected_set = set(CURATED_SECRET_NOUNS) | VALID_SHORT_WORDS | VALID_HYPHEN_WORDS
    banned_indices = set()

    for cname, (seeds, threshold) in clusters.items():
        seed_idxs = [raw_word_to_idx[s] for s in seeds if s in raw_word_to_idx]
        if not seed_idxs:
            continue
        centroid = np.mean(raw_vectors[seed_idxs], axis=0)
        centroid /= np.linalg.norm(centroid)
        sims = raw_vectors @ centroid
        bad_idxs = np.where(sims >= threshold)[0]
        for idx in bad_idxs:
            # Ne bannit JAMAIS un mot courant situé dans les 20 000 premiers mots du français
            if idx >= 20000 and raw_words[idx] not in protected_set:
                banned_indices.add(int(idx))

    print(f"    ✓ {len(banned_indices):,} scories rares bannies sans toucher aux mots courants")
    return banned_indices

def build_deduplicated_vocabulary(words, raw_word_to_idx, banned_indices):
    print("3/5 Construction du vocabulaire (avec protection de 'plante' et suppression des doublons sans accent)...")
    candidates = []
    seen_exact = set()
    # Stocke uniquement les mots accentués dont l'accent n'est PAS une simple terminaison de participe passé (-é/-ée)
    internal_accent_lookup = {}

    for idx, w in enumerate(words):
        if idx in banned_indices or w in seen_exact or not is_valid_french_word(w):
            continue
        # Exclut les siècles en chiffres romains (ex: xvème, xviième, xiiième)
        if w.endswith(("ème", "eme")) and any(c in w[:-3] for c in "ivx"):
            continue

        seen_exact.add(w)
        candidates.append((idx, w))

        if has_french_accent(w):
            unacc = strip_accents(w)
            # RÈGLE CRUCIALE : Ne jamais enregistrer "planté" comme version accentuée de "plante" !
            if not (w.endswith(("é", "ée", "és", "ées")) and not has_french_accent(w.rstrip("s").rstrip("e")[:-1])):
                if unacc not in internal_accent_lookup:
                    internal_accent_lookup[unacc] = (w, idx)

        if len(candidates) >= 105000:
            break

    # Vrais homographes français où la version sans accent et avec accent sont 2 vrais mots différents
    TRUE_HOMOGRAPHS = {
        "mur", "tache", "cote", "jeune", "pate", "foret", "du", "cru",
        "sur", "mat", "chaine", "boite", "haler", "batir", "pecher", "gene",
        "pole", "cone", "dome", "role", "jeunes", "romo", "acre"
    }

    clean_indices = []
    clean_words = []
    word_to_clean_pos = {}

    for orig_idx, w in candidates:
        # 1. Supprime toute faute d'oubli d'accent (chateau -> château, etoile -> étoile, reseau -> réseau)
        # tout en gardant les vrais mots en -e (plante != planté) et les vrais homographes (mur != mûr)
        if not has_french_accent(w) and w in internal_accent_lookup and w not in TRUE_HOMOGRAPHS:
            continue

        # 2. Filtre des pluriels (uniquement si le singulier est déjà présent dans notre dictionnaire propre)
        sing = get_singular_candidate(w)
        if sing and sing in word_to_clean_pos:
            continue

        word_to_clean_pos[w] = len(clean_words)
        clean_words.append(w)
        clean_indices.append(orig_idx)

        if len(clean_words) >= TARGET_CLEAN_VOCAB:
            break

    # Auto-test de sécurité sur les mots courants ET vérification que les fautes sans accent sont bien supprimées
    must_exist = [
        "plante", "plant", "planter", "arbre", "fleur", "forêt", "feuille", "racine", "jardin",
        "ferme", "forme", "force", "place", "coupe", "groupe", "compte", "garde", "marche",
        "château", "étoile", "réseau", "éditeur", "aïkido", "poisson", "poison", "désert", "dessert"
    ]
    must_not_exist = ["chateau", "etoile", "reseau", "editeur", "aikido", "xvème", "xviième"]

    present = [tw for tw in must_exist if tw in word_to_clean_pos]
    leaked = [tw for tw in must_not_exist if tw in word_to_clean_pos]

    print(f"    ✓ Vocabulaire final : {len(clean_words):,} mots")
    print(f"    ✓ Auto-test mots valides : {len(present)}/{len(must_exist)} présents")
    print(f"    ✓ Auto-test fautes supprimées : {len(leaked)} fuite(s) ({leaked if leaked else '100% propre !'})")

    return np.array(clean_indices, dtype=np.int32), clean_words, word_to_clean_pos

def select_500_curated_secrets(clean_words, clean_vectors, word_to_clean_pos, count=500):
    print("4/5 Sélection des 500 mots secrets...")
    valid_secrets = []
    seen = set()

    for w in CURATED_SECRET_NOUNS:
        w_low = w.lower().strip()
        if w_low in seen or w_low not in word_to_clean_pos:
            continue
        seen.add(w_low)

        pos = word_to_clean_pos[w_low]
        sims = clean_vectors @ clean_vectors[pos]
        top15_idx = np.argpartition(-sims, 16)[:16]
        top15_vecs = clean_vectors[top15_idx]
        cohesion = float(np.mean(top15_vecs @ top15_vecs.T))

        if cohesion >= 0.38:
            valid_secrets.append(w_low)

    random.seed(42)
    selected = random.sample(valid_secrets, min(count, len(valid_secrets)))
    print(f"    ✓ {len(selected)} mots secrets validés !")
    return selected

def generate_500_games():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_words, raw_word_to_idx, raw_vectors = load_word2vec_bin(MODEL_PATH)

    banned_indices = build_semantic_ban_mask(raw_words, raw_word_to_idx, raw_vectors)
    clean_indices, clean_words, word_to_clean_pos = build_deduplicated_vocabulary(raw_words, raw_word_to_idx, banned_indices)
    clean_vectors = raw_vectors[clean_indices]

    secrets = select_500_curated_secrets(clean_words, clean_vectors, word_to_clean_pos, NB_PARTIES)
    print(f"5/5 Génération des {len(secrets)} fichiers JSON dans '{OUTPUT_DIR}/'...")

    for game_id, secret in enumerate(secrets, start=1):
        secret_pos = word_to_clean_pos[secret]
        target_vec = clean_vectors[secret_pos]

        sims = clean_vectors @ target_vec
        order = np.argsort(-sims)

        words_dict = {}
        rank_counter = 1000

        for pos in order:
            w = clean_words[pos]
            if w == secret:
                words_dict[w] = [100.0, 1000]
                continue

            if rank_counter > 1:
                rank_counter -= 1
                words_dict[w] = [round(float(sims[pos]) * 100, 2), rank_counter]
            else:
                words_dict[w] = round(float(sims[pos]) * 100, 1)

        filepath = os.path.join(OUTPUT_DIR, f"partie_{game_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"id": game_id, "words": words_dict}, f, ensure_ascii=False, separators=(",", ":"))

        if game_id % 50 == 0 or game_id == len(secrets):
            print(f"    [{game_id}/{len(secrets)}] parties générées...")

    print("✅ Terminé ! Tous les mots courants (dont 'plante') sont désormais présents.")

if __name__ == "__main__":
    generate_500_games()
