# config.py

# ------------------------------------------------------------------------
# Configuration: stores to ignore
# ------------------------------------------------------------------------
IGNORED_STORES = [
    # CURRYS STORES
    "04944: CURRYS ONLINE 'OMS VIRTUAL'",
    "04947: PCW ONLINE OMS VIRTUAL",
    "04985: IRELAND ONLINE SMALLBOX DIRECT",
    "07272: ONLINE CSC INVESTIGATIONS",
    "05088: PCWB DIRECT SALE 'OMS VIRTUAL'",
    "05089: PCWB ONLINE CUSTOMER RETURNS",
    "07099: NEWARK RDC",
    "07800: NATIONAL RETURNS",
    "04943: CURRYS TELESALES 'OMS VIRTUAL'",
    # TOOLSTATION STORES
    "(CLOSED) BOURNEMOUTH TOOLSTATION",
    "(CLOSED) BRIDGWATER TOOLSTATION",
    "(CLOSED) DUMFRIES TOOLSTATION",
    "(CLOSED) EDMONTON TOOLSTATION",
    "(CLOSED) HOLMES CHAPEL TOOLSTATION",
    "(CLOSED) BRIMSDOWN TOOLSTATION",
    "(CLOSED) NUNEATON TOOLSTATION",
    "(CLOSED) STIRCHLEY TOOLSTATION",
    "(CLOSED) SLOUGH TOOLSTATION",
    "(CLOSED) TAUNTON TOOLSTATION",
    "(CLOSED) FOLKESTONE TOOLSTATION",
    "(CLOSED) HOVE DAVIGDOR ROAD TOOLSTATION",
    "(CLOSED) WIMBLEDON TOOLSTATION",
    "(CLOSED) HEREFORD TOOLSTATION",
    "(CLOSED) HUNTINGDON TOOLSTATION",
    "(CLOSED) SHEPTON MALLET TOOLSTATION",
    "(CLOSED) MALVERN TOOLSTATION",
    "(CLOSED) CHADWELL HEATH TOOLSTATION",
    "(CLOSED) STOCKPORT TOOLSTATION",
    "(CLOSED) PERRY BARR TOOLSTATION",
    "(CLOSED) BOREHAMWOOD TOOLSTATION",
    "(CLOSED) CARDIFF OCEAN WAY TOOLSTATION",
    "(CLOSED) OXFORD BOTLEY TOOLSTATION",
    "(CLOSED) KINGSTON UPON THAMES TOOLSTATION",
    "(CLOSED) BICESTER TOOLSTATION",
    "(CLOSED) EXETER TOOLSTATION",
    "(CLOSED) CLEARANCE CORNER TOOLSTATION",
    "CONTACT CENTRE TOOLSTATION",
    "WEBSITE TOOLSTATION",
    "CONTACT CENTRE TOOLSTATION",
    "WEBSITE TOOLSTATION",
    "WEBSITE TOOLSTATION",
    "WEBSITE TOOLSTATION",
    "WEBSITE TOOLSTATION",
    # SCREWFIX STORES
    "WWW.SCREWFIX.COM"
    "SCREWFIX LIVE"
    "SCREWFIX.IE"
]

# ------------------------------------------------------------------------
# Configuration: SKUs to rename
# ------------------------------------------------------------------------
SKU_MAPPING = {
    "226-800604901": "Air Bundle",
    "226-802600101": "Air",
    "226-802604501": "POS Lite",
    "226-802610001": "Solo",
    "226-802620001": "Solo & Printer",
    "226-902600701": "3G",
    "386803    :  SP6 SP6 POS L &SOLO": "POS Lite",
    "537815    :  SP6 SP6 SUMUP  SOLO": "Solo",
    "604611    :  SP6 SUMUP AIR": "Air",
    "660513    :  SP6 AIR BUNDL E": "Air Bundle",
    "626938    :  SP6 SUMUPSOLL OPRNTER": "Solo & Printer",
    "613971    :  SP6 SP6 SUMUP  3G+ PK": "3G PK",
    "SUMUP AIR CRADLE BUNDLE PK1": "Air Bundle",
    "SUMUP SOLO                PK1": "Solo",
    "SUMUP 3G PAYMENT KIT/PRINTER PK1 DNO": "3G PK",
    "DX SUMUP AIR CARD PAYMENT DEVICE PK1": "Air",
    "DX SUMUP 3G CARD PAYMENT DEVICE PK1 DNO": "3G",
    "3593051055-SumUp Air Card Reader-A Smarter Way to Get Paid": "Air",
    "3597012311-SumUp Solo Smart Card Terminal-": "Solo",
    "3597012312-SumUp AirPlus Cradle Bundle-": "Air Bundle",
    "3597012314-SumUp POS Lite Solo Bundle-": "POS Lite",
    "1250000000-SumUp Solo+ Printer-Payment Card Reader": "Solo & Printer",
    "SUMUP AIR CARD READER EACH": "Air",
    "SUMUP SOLO SMART CARD TERMINAL EACH": "Solo",
    "SOLO & PRINTER BUNDLE RETAIL UK EACH": "Solo & Printer",
    "POS LITE & SOLO BUNDLE UK EACH": "POS Lite",
    "226-RDR-SUL-004": "Solo Lite",
    "226-BUN-SUL-003": "Solo Lite Bundle",
    "SUM UP AIR CONTACTLESS CARD READER": "Air",
    "SUMUP SOLO SMART CARD TERMINAL": "Solo",
}

# ------------------------------------------------------------------------
# Configuration: SKUs to ignore entirely
# ------------------------------------------------------------------------
IGNORED_SKUS = [
    "SUMUP 3G PAYMENT KIT/PRINTER PK1 DNO",
    "DX SUMUP 3G CARD PAYMENT DEVICE PK1 DNO",
    "613971    :  SP6 SP6 SUMUP  3G+ PK",
    "226-902600701",
    "3597012300-SumUp Air Cradle-Docking Station White",
    "3597012310-SumUp Air Reader and Cradle-Bundle White",
    "3597016543-SumUp 3G + Wifi Payment Reader-Standalone Card White",
    "3597016544-SumUp 3G Payment Kit-",
    "3597012301-Solo SumUp Card Reader-",
    "3597012313-Sumup Point of Sale Lite-",
    "SUMUP AIR CHARGING CRADLE CHARGER EACH",
    "SUMUP 3G+ WIFI CARD READER PAYMENT KIT EACH",
    "SUMUP 3G+ WIFI CARD READER EACH",
]
