# -*- coding: utf-8 -*-
# This parser uses the dictionararies defined by 
#

dict_projections = {
    "WGS84": 4326,
    "Gauss-Krüger1": 5520,
    "Gauss-Krüger2": 31466,
    "Gauss-Krüger3": 31467,
    "Gauss-Krüger4": 31468,
    "Gauss-Krüger5": 31469,
    "ETRS32 8stellig": 102329,
    "ETRS32 7stellig": 102328,
    "ETRS32 6stellig": 25832,
    "ETRS33 8stellig": 102359,
    "ETRS33 7stellig": 102360,
    "ETRS33 6stellig": 25833,
    "Kein Projektionssystem": "NONE",
    }

dict_labels = {
# Textinormationen
    "@T": "manual_notes",
    "01": "manual_notes",
    "02": "not_defined",
    "03": "not_defined",
    "04": "not_defined",
    "05": "not_defined",
    "06": "not_defined",
    "07": "not_defined",
    "08": "not_defined",
    "09": "not_defined",
    "10": "not_defined",
# Allgemeines
    "11": "pointId",
    "12": "serialID",
    "13": "identInstrument",
    "14": "not_defined",
    "15": "not_defined",
    "16": "stationID",
    "17": "date",
    "18": "time1",
    "19": "time2",
# Richtungen
    "20": "angularAccuracy",
    "21": "hzAngle",
    "22": "vertAngle",
    "23": "not_defined",
    "24": "targetAngle",
    "25": "AngleDifference",
    "26": "rotationAngle",
    "27": "targetVertAngle",
    "28": "vertDifference",
    "29": "not_defined",
# Distanzen
    "30": "not_defined",
    "31": "slopeDist",
    "32": "hzDist",
    "33": "HeightDiff",
    "34": "targetDist",
    "35": "DistDiffHz",
    "36": "targetDiffHeight",
    "37": "HeightDiff",
    "38": "targetSlopeDist",
    "39": "DistDiffSlope",
# Codeblock
    "40": "not_defined",
    "41": "CodeBlockID",
    "42": "stationID",
    "43": "stationHeight",
    "44": "Info3",
    "45": "Info4",
    "46": "Info5",
    "47": "Info6",
    "48": "Info7",
    "49": "Info8",
# Distanz-Zusatzinformationen
    "50": "not_defined",
    "51": "constDist",
    "52": "constPrism",
    "53": "MeasureNr",
    "54": "Signalqual",
    "55": "refractCoef",
    "56": "relHumidity",
    "57": "SigDist",
    "58": "PrismConstant",
    "59": "PPM",
# Richtungs-Zusatzinformationen
    "60": "not_defined",
    "61": "longInclin",
    "62": "transInclin",
    "63": "standAxisTilt",
    "64": "standAxisAz",
    "65": "not_defined",
    "66": "not_defined",
    "67": "not_defined",
    "68": "not_defined",
    "69": "not_defined",
# Bemerkungen
    "70": "not_defined",
    "71": "pointCode",
    "72": "note2",
    "73": "note3",
    "74": "note4",
    "75": "note5",
    "76": "note6",
    "77": "note7",
    "78": "note8",
    "79": "note9",
# Koordinaten
    "80": "not_defined",
    "81": "targetY",
    "82": "targetX",
    "83": "targetZ",
    "84": "stationY",
    "85": "stationX",
    "86": "stationZ",
    "87": "reflectorZ",
    "88": "instrumentZ",
    "89": "not_defined",
# Rohdaten
    "90": "not_defined",
    "91": "DirectionUncorr",
    "92": "VerticalUncorr",
    "93": "inclinationLenght",
    "94": "inclinationCross",
    "95": "not_defined",
    "96": "not_defined",
    "97": "not_defined",
    "98": "not_defined",
    "99": "not_defined",
    }

dict_formats = {
    "@T": "TEXT",
    "01": "TEXT",
    "02": "TEXT",
    "03": "TEXT",
    "04": "TEXT",
    "05": "TEXT",
    "06": "TEXT",
    "07": "TEXT",
    "08": "TEXT",
    "09": "TEXT",
    "10": "TEXT",
    "11": "TEXT",
    "12": "TEXT",
    "13": "TEXT",
    "14": "TEXT",
    "15": "TEXT",
    "16": "TEXT",
    "40": "TEXT",
    "41": "TEXT",
    "42": "TEXT",
    "43": "TEXT",
    "44": "TEXT",
    "45": "TEXT",
    "46": "TEXT",
    "47": "TEXT",
    "48": "TEXT",
    "49": "TEXT",
    "70": "TEXT",
    "71": "TEXT",
    "72": "TEXT",
    "73": "TEXT",
    "74": "TEXT",
    "75": "TEXT",
    "76": "TEXT",
    "77": "TEXT",
    "78": "TEXT",
    "79": "TEXT",
    "17": "DATE",
    "18": "DATE",
    "19": "DATE",
    "20": "DOUBLE",
    "21": "DOUBLE",
    "22": "DOUBLE",
    "23": "DOUBLE",
    "24": "DOUBLE",
    "25": "DOUBLE",
    "26": "DOUBLE",
    "27": "DOUBLE",
    "28": "DOUBLE",
    "29": "DOUBLE",
    "30": "DOUBLE",
    "31": "DOUBLE",
    "32": "DOUBLE",
    "33": "DOUBLE",
    "34": "DOUBLE",
    "35": "DOUBLE",
    "36": "DOUBLE",
    "37": "DOUBLE",
    "38": "DOUBLE",
    "39": "DOUBLE",
    "50": "DOUBLE",
    "51": "DOUBLE",
    "52": "DOUBLE",
    "53": "DOUBLE",
    "54": "DOUBLE",
    "55": "DOUBLE",
    "56": "DOUBLE",
    "57": "DOUBLE",
    "58": "DOUBLE",
    "59": "DOUBLE",
    "60": "DOUBLE",
    "61": "DOUBLE",
    "62": "DOUBLE",
    "63": "DOUBLE",
    "64": "DOUBLE",
    "65": "DOUBLE",
    "66": "DOUBLE",
    "67": "DOUBLE",
    "68": "DOUBLE",
    "69": "DOUBLE",
    "80": "DOUBLE",
    "81": "DOUBLE",
    "82": "DOUBLE",
    "83": "DOUBLE",
    "84": "DOUBLE",
    "85": "DOUBLE",
    "86": "DOUBLE",
    "87": "DOUBLE",
    "88": "DOUBLE",
    "89": "DOUBLE",
    "90": "DOUBLE",
    "91": "DOUBLE",
    "92": "DOUBLE",
    "93": "DOUBLE",
    "94": "DOUBLE",
    "95": "DOUBLE",
    "96": "DOUBLE",
    "97": "DOUBLE",
    "98": "DOUBLE",
    "99": "DOUBLE",
    }


dict_units_attributes_digits = {
    "0": "meter_1mm",
    "1": "feet",
    "2": "gon",
    "3": "degree_decimal",
    "4": "degree_sexagesimal",
    "5": "mil",
    "6": "meter_1_10mm",
    "7": "feet_1_10t",
    "8": "meter_1_100mm",
    ".": None
    }

# number of decimal places for each type of unit
dict_units_digits = {
    "0": 3,
     "1": 3,
     "2": 5,
     "3": 5,
     "4": 5,
     "5": 4,
     "6": 4,
     "7": 4,
     "8": 5,
     "9": 0,
     ".": 0,
    }

# dividers required to put the point where it belongs
dict_units_dividers = {
    "0": 100,
     "1": 100,
     "2": 10000,
     "3": 10000,
     "4": 10000,
     "5": 1000,
     "6": 1000,
     "7": 1000,
     "8": 10000,
     "9": 1,
     ".": 1,
    }

dict_typeConversions = {
    "TEXT": str,
    "DOUBLE": float,
    "DATE": complex,
    "LONG": int,
    }

def parse(line):
    extracted = {}
    units = {}
    # Leica supports two different formats: GSI-8 and GSI-16.
    # The numbers represent the available precision for storing values.
    # GSI-16 is identified by prefixing the dataset with an asterisk character
    if len(line) <= 2:
        return extracted, units
    if line[0] == "*":
        precision = 16
        line = line[1:]
    else:
        precision = 8
    extracted['precision'] = precision
    for part in line.split():
        identifier = part[:2]
        idExtension = part[2]
        compensatorInfo = part[3]
        sourceInfo = part[4]
        unitInfo = part[5]
        signInfo = part[6]
        value = part[7:]

        # The first two places define the content of a part, which in turn defines the data type of the value
        label = dict_labels[identifier]
        baseType = dict_formats[identifier]
        units[label] = dict_units_attributes_digits[unitInfo]
        try:
            # strings are simple, the require no further treatment before passing on, so they are exempt from processing:
            if not baseType == "TEXT":
                # everything else has to be cast to another type:
                value = dict_typeConversions[baseType](value)
                # Datetimes are now considered done, numbers still have to be adjusted for sign and precision:
                if not baseType == "DATE":
                    # positive values are identified by a '+' sign at the 7th place of a word

                    if not signInfo == "+":
                        value *= -1
                    value /= dict_units_dividers[unitInfo]
                    
            # converted values are labeled and written to a dict
            extracted[label] = value
        except ValueError:
            pass
    return extracted, units


if __name__ == "__main__":
    testLine = "*11....+0000000000000306 21.022+0000000002264250 22.022+0000000009831450 31..00+0000000000002316 81..00+0000000565386572 82..00+0000005924616673 83..00+0000000000005367 87..10+0000000000000000 \r\n"
    parsed, units = parse(testLine)
    print(list(parsed.keys()))
    print(parsed['precision'])
    print(parsed['targetX'], parsed['targetY'], parsed['targetZ'])
    print(units['targetX'], units['targetY'], units['targetZ'])
    print(parsed['pointId'])
