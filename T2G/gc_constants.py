GRC_OK = 0                             # Function successfully completed.
GRC_UNDEFINED = 1                      # Unknown error, result unspecified.
GRC_IVPARAM = 2                        # Invalid parameter detected. Result unspecified.
GRC_IVRESULT = 3                       # Invalid result.
GRC_FATAL = 4                          # Fatal error.
GRC_NOT_IMPL = 5                       # Not implemented yet.
GRC_TIME_OUT = 6                       # Function execution timed out. Result unspecified.
GRC_SET_INCOMPL = 7                    # Parameter setup for subsystem is incomplete.
GRC_ABORT = 8                          # Function execution has been aborted.
GRC_NOMEMORY = 9                       # Fatal error - not enough memory.
GRC_NOTINIT = 10                       # Fatal error - subsystem not initialized.
GRC_SHUT_DOWN = 12                     # Subsystem is down.
GRC_SYSBUSY = 13                       # System busy/already in use of another process. Cannot execute function.
GRC_HWFAILURE = 14                     # Fatal error - hardware failure.
GRC_ABORT_APPL = 15                    # Execution of application has been aborted (SHIFT-ESC).
GRC_LOW_POWER = 16                     # Operation aborted - insufficient power supply level.
GRC_IVVERSION = 17                     # Invalid version of file, ...
GRC_BATT_EMPTY = 18                    # Battery empty
GRC_NO_EVENT = 20                      # no event pending.
GRC_OUT_OF_TEMP = 21                   # out of temperature range
GRC_INSTRUMENT_TILT = 22               # instrument tilting out of range
GRC_COM_SETTING = 23                   # communication error
GRC_NO_ACTION = 24                     # GRC_TYPE Input 'do no action'
GRC_SLEEP_MODE = 25                    # Instr. run into the sleep mode
GRC_NOTOK = 26                         # Function not successfully completed.
GRC_NA = 27                            # Not available
GRC_OVERFLOW = 28                      # Overflow error
GRC_STOPPED = 29                       # System or subsystem has been stopped
GRC_ANG_ERROR = 257                    # Angles and Inclinations not valid
GRC_ANG_INCL_ERROR = 258               # inclinations not valid
GRC_ANG_BAD_ACC = 259                  # value accuracies not reached
GRC_ANG_BAD_ANGLE_ACC = 260            # angle-accuracies not reached
GRC_ANG_BAD_INCLIN_ACC = 261           # inclination accuracies not reached
GRC_ANG_WRITE_PROTECTED = 266          # no write access allowed
GRC_ANG_OUT_OF_RANGE = 267             # value out of range
GRC_ANG_IR_OCCURED = 268               # function aborted due to interrupt
GRC_ANG_HZ_MOVED = 269                 # hz moved during incline measurement
GRC_ANG_OS_ERROR = 270                 # troubles with operation system
GRC_ANG_DATA_ERROR = 271               # overflow at parameter values
GRC_ANG_PEAK_CNT_UFL = 272             # too less peaks
GRC_ANG_TIME_OUT = 273                 # reading timeout
GRC_ANG_TOO_MANY_EXPOS = 274           # too many exposures wanted
GRC_ANG_PIX_CTRL_ERR = 275             # picture height out of range
GRC_ANG_MAX_POS_SKIP = 276             # positive exposure dynamic overflow
GRC_ANG_MAX_NEG_SKIP = 277             # negative exposure dynamic overflow
GRC_ANG_EXP_LIMIT = 278                # exposure time overflow
GRC_ANG_UNDER_EXPOSURE = 279           # picture underexposured
GRC_ANG_OVER_EXPOSURE = 280            # picture overexposured
GRC_ANG_TMANY_PEAKS = 300              # too many peaks detected
GRC_ANG_TLESS_PEAKS = 301              # too less peaks detected
GRC_ANG_PEAK_TOO_SLIM = 302            # peak too slim
GRC_ANG_PEAK_TOO_WIDE = 303            # peak to wide
GRC_ANG_BAD_PEAKDIFF = 304             # bad peak difference
GRC_ANG_UNDER_EXP_PICT = 305           # too less peak amplitude
GRC_ANG_PEAKS_INHOMOGEN = 306          # inhomogeneous peak amplitudes
GRC_ANG_NO_DECOD_POSS = 307            # no peak decoding possible
GRC_ANG_UNSTABLE_DECOD = 308           # peak decoding not stable
GRC_ANG_TLESS_FPEAKS = 309             # too less valid finepeaks
GRC_ATA_NOT_READY = 512                # ATR-System is not ready.
GRC_ATA_NO_RESULT = 513                # Result isn't available yet.
GRC_ATA_SEVERAL_TARGETS = 514          # Several Targets detected.
GRC_ATA_BIG_SPOT = 515                 # Spot is too big for analyse.
GRC_ATA_BACKGROUND = 516               # Background is too bright.
GRC_ATA_NO_TARGETS = 517               # No targets detected.
GRC_ATA_NOT_ACCURAT = 518              # Accuracy worse than asked for.
GRC_ATA_SPOT_ON_EDGE = 519             # Spot is on the edge of the sensing area.
GRC_ATA_BLOOMING = 522                 # Blooming or spot on edge detected.
GRC_ATA_NOT_BUSY = 523                 # ATR isn't in a continuous mode.
GRC_ATA_STRANGE_LIGHT = 524            # Not the spot of the own target illuminator.
GRC_ATA_V24_FAIL = 525                 # Communication error to sensor (ATR).
GRC_ATA_DECODE_ERROR = 526             # Received Arguments cannot be decoded
GRC_ATA_HZ_FAIL = 527                  # No Spot detected in Hz-direction.
GRC_ATA_V_FAIL = 528                   # No Spot detected in V-direction.
GRC_ATA_HZ_STRANGE_L = 529             # Strange light in Hz-direction.
GRC_ATA_V_STRANGE_L = 530              # Strange light in V-direction.
GRC_ATA_SLDR_TRANSFER_PENDING = 531    # On multiple ATA_SLDR_OpenTransfer.
GRC_ATA_SLDR_TRANSFER_ILLEGAL = 532    # No ATA_SLDR_OpenTransfer happened.
GRC_ATA_SLDR_DATA_ERROR = 533          # Unexpected data format received.
GRC_ATA_SLDR_CHK_SUM_ERROR = 534       # Checksum error in transmitted data.
GRC_ATA_SLDR_ADDRESS_ERROR = 535       # Address out of valid range.
GRC_ATA_SLDR_INV_LOADFILE = 536        # Firmware file has invalid format.
GRC_ATA_SLDR_UNSUPPORTED = 537         # Current (loaded) firmware doesn't support upload.
GRC_ATA_PS_NOT_READY = 538             # PS-System is not ready.
GRC_ATA_ATR_SYSTEM_ERR = 539           # ATR system error
GRC_EDM_SYSTEM_ERR = 769               # Fatal EDM sensor error. See for the exact reason the original EDM sensor error number. In the most cases a service problem.
GRC_EDM_INVALID_COMMAND = 770          # Invalid command or unknown command, see command syntax.
GRC_EDM_BOOM_ERR = 771                 # Boomerang error.
GRC_EDM_SIGN_LOW_ERR = 772             # Received signal to low, prism to far away, or natural barrier, bad environment, etc.
GRC_EDM_DIL_ERR = 773                  # obsolete
GRC_EDM_SIGN_HIGH_ERR = 774            # Received signal to strong, prism to near, stranger light effect.
GRC_EDM_TIMEOUT = 775                  # Timeout, measuring time exceeded (signal too weak, beam interrupted,..)
GRC_EDM_FLUKT_ERR = 776                # to much turbulences or distractions
GRC_EDM_FMOT_ERR = 777                 # filter motor defective
GRC_EDM_DEV_NOT_INSTALLED = 778        # Device like EGL, DL is not installed.
GRC_EDM_NOT_FOUND = 779                # Search result invalid. For the exact explanation, see in the description of the called function.
GRC_EDM_ERROR_RECEIVED = 780           # Communication ok, but an error reported from the EDM sensor.
GRC_EDM_MISSING_SRVPWD = 781           # No service password is set.
GRC_EDM_INVALID_ANSWER = 782           # Communication ok, but an unexpected answer received.
GRC_EDM_SEND_ERR = 783                 # Data send error, sending buffer is full.
GRC_EDM_RECEIVE_ERR = 784              # Data receive error, like parity buffer overflow.
GRC_EDM_INTERNAL_ERR = 785             # Internal EDM subsystem error.
GRC_EDM_BUSY = 786                     # Sensor is working already, abort current measuring first.
GRC_EDM_NO_MEASACTIVITY = 787          # No measurement activity started.
GRC_EDM_CHKSUM_ERR = 788               # Calculated checksum, resp. received data wrong (only in binary communication mode possible).
GRC_EDM_INIT_OR_STOP_ERR = 789         # During start up or shut down phase an error occured. It is saved in the DEL buffer.
GRC_EDM_SRL_NOT_AVAILABLE = 790        # Red laser not available on this sensor HW.
GRC_EDM_MEAS_ABORTED = 791             # Measurement will be aborted (will be used for the laser security)
GRC_EDM_SLDR_TRANSFER_PENDING = 798    # Multiple OpenTransfer calls.
GRC_EDM_SLDR_TRANSFER_ILLEGAL = 799    # No open transfer happened.
GRC_EDM_SLDR_DATA_ERROR = 800          # Unexpected data format received.
GRC_EDM_SLDR_CHK_SUM_ERROR = 801       # Checksum error in transmitted data.
GRC_EDM_SLDR_ADDR_ERROR = 802          # Address out of valid range.
GRC_EDM_SLDR_INV_LOADFILE = 803        # Firmware file has invalid format.
GRC_EDM_SLDR_UNSUPPORTED = 804         # Current (loaded) firmware doesn't support upload.
GRC_EDM_UNKNOW_ERR = 808               # Undocumented error from the EDM sensor, should not occur.
GRC_EDM_DISTRANGE_ERR = 818            # Out of distance range (dist too small or large)
GRC_EDM_SIGNTONOISE_ERR = 819          # Signal to noise ratio too small
GRC_EDM_NOISEHIGH_ERR = 820            # Noise to high
GRC_EDM_PWD_NOTSET = 821               # Password is not set
GRC_EDM_ACTION_NO_MORE_VALID = 822     # Elapsed time between prepare und start fast measurement for ATR to long
GRC_EDM_MULTRG_ERR = 823               # Possibly more than one target (also a sensor error)
GRC_TMC_NO_FULL_CORRECTION = 1283      # Warning: measurement without full correction
GRC_TMC_ACCURACY_GUARANTEE = 1284      # Info: accuracy can not be guarantee
GRC_TMC_ANGLE_OK = 1285                # Warning: only angle measurement valid
GRC_TMC_ANGLE_NOT_FULL_CORR = 1288     # Warning: only angle measurement valid but without full correction
GRC_TMC_ANGLE_NO_ACC_GUARANTY = 1289   # Info: only angle measurement valid but accuracy can not be guarantee
GRC_TMC_ANGLE_ERROR = 1290             # Error: no angle measurement
GRC_TMC_DIST_PPM = 1291                # Error: wrong setting of PPM or MM on EDM
GRC_TMC_DIST_ERROR = 1292              # Error: distance measurement not done (no aim, etc.)
GRC_TMC_BUSY = 1293                    # Error: system is busy (no measurement done)
GRC_TMC_SIGNAL_ERROR = 1294            # Error: no signal on EDM (only in signal mode)
GRC_BMM_XFER_PENDING = 2305            # Loading process already opened
GRC_BMM_NO_XFER_OPEN = 2306            # Transfer not opened
GRC_BMM_UNKNOWN_CHARSET = 2307         # Unknown character set
GRC_BMM_NOT_INSTALLED = 2308           # Display module not present
GRC_BMM_ALREADY_EXIST = 2309           # Character set already exists
GRC_BMM_CANT_DELETE = 2310             # Character set cannot be deleted
GRC_BMM_MEM_ERROR = 2311               # Memory cannot be allocated
GRC_BMM_CHARSET_USED = 2312            # Character set still used
GRC_BMM_CHARSET_SAVED = 2313           # Charset cannot be deleted or is protected
GRC_BMM_INVALID_ADR = 2314             # Attempt to copy a character block outside the allocated memory
GRC_BMM_CANCELANDADR_ERROR = 2315      # Error during release of allocated memory
GRC_BMM_INVALID_SIZE = 2316            # Number of bytes specified in header does not match the bytes read
GRC_BMM_CANCELANDINVSIZE_ERROR = 2317  # Allocated memory could not be released
GRC_BMM_ALL_GROUP_OCC = 2318           # Max. number of character sets already loaded
GRC_BMM_CANT_DEL_LAYERS = 2319         # Layer cannot be deleted
GRC_BMM_UNKNOWN_LAYER = 2320           # Required layer does not exist
GRC_BMM_INVALID_LAYERLEN = 2321        # Layer length exceeds maximum
GRC_COM_ERO = 3072                     # Initiate Extended Runtime Operation (ERO).
GRC_COM_CANT_ENCODE = 3073             # Cannot encode arguments in client.
GRC_COM_CANT_DECODE = 3074             # Cannot decode results in client.
GRC_COM_CANT_SEND = 3075               # Hardware error while sending.
GRC_COM_CANT_RECV = 3076               # Hardware error while receiving.
GRC_COM_TIMEDOUT = 3077                # Request timed out.
GRC_COM_WRONG_FORMAT = 3078            # Packet format error.
GRC_COM_VER_MISMATCH = 3079            # Version mismatch between client and server.
GRC_COM_CANT_DECODE_REQ = 3080         # Cannot decode arguments in server.
GRC_COM_PROC_UNAVAIL = 3081            # Unknown RPC, procedure ID invalid.
GRC_COM_CANT_ENCODE_REP = 3082         # Cannot encode results in server.
GRC_COM_SYSTEM_ERR = 3083              # Unspecified generic system error.
GRC_COM_FAILED = 3085                  # Unspecified error.
GRC_COM_NO_BINARY = 3086               # Binary protocol not available.
GRC_COM_INTR = 3087                    # Call interrupted.
GRC_COM_REQUIRES_8DBITS = 3090         # Protocol needs 8bit encoded characters.
GRC_COM_TR_ID_MISMATCH = 3093          # TRANSACTIONS ID mismatch error.
GRC_COM_NOT_GEOCOM = 3094              # Protocol not recognizable.
GRC_COM_UNKNOWN_PORT = 3095            # (WIN) Invalid port address.
GRC_COM_ERO_END = 3099                 # ERO is terminating.
GRC_COM_OVERRUN = 3100                 # Internal error: data buffer overflow.
GRC_COM_SRVR_RX_CHECKSUM_ERRR = 3101   # Invalid checksum on server side received.
GRC_COM_CLNT_RX_CHECKSUM_ERRR = 3102   # Invalid checksum on client side received.
GRC_COM_PORT_NOT_AVAILABLE = 3103      # (WIN) Port not available.
GRC_COM_PORT_NOT_OPEN = 3104           # (WIN) Port not opened.
GRC_COM_NO_PARTNER = 3105              # (WIN) Unable to find TPS.
GRC_COM_ERO_NOT_STARTED = 3106         # Extended Runtime Operation could not be started.
GRC_COM_CONS_REQ = 3107                # Att to send cons reqs
GRC_COM_SRVR_IS_SLEEPING = 3108        # TPS has gone to sleep. Wait and try again.
GRC_COM_SRVR_IS_OFF = 3109             # TPS has shut down. Wait and try again.
GRC_AUT_TIMEOUT = 8704                 # Position not reached
GRC_AUT_DETENT_ERROR = 8705            # Positioning not possible due to mounted EDM
GRC_AUT_ANGLE_ERROR = 8706             # Angle measurement error
GRC_AUT_MOTOR_ERROR = 8707             # Motorisation error
GRC_AUT_INCACC = 8708                  # Position not exactly reached
GRC_AUT_DEV_ERROR = 8709               # Deviation measurement error
GRC_AUT_NO_TARGET = 8710               # No target detected
GRC_AUT_MULTIPLE_TARGETS = 8711        # Multiple target detected
GRC_AUT_BAD_ENVIRONMENT = 8712         # Bad environment conditions
GRC_AUT_DETECTOR_ERROR = 8713          # Error in target acquisition
GRC_AUT_NOT_ENABLED = 8714             # Target acquisition not enabled
GRC_AUT_CALACC = 8715                  # ATR-Calibration failed
GRC_AUT_ACCURACY = 8716                # Target position not exactly reached
GRC_AUT_DIST_STARTED = 8717            # Info: dist. measurement has been started
GRC_AUT_SUPPLY_TOO_HIGH = 8718         # external Supply voltage is too high
GRC_AUT_SUPPLY_TOO_LOW = 8719          # int. or ext. Supply voltage is too low
GRC_AUT_NO_WORKING_AREA = 8720         # working area not set
GRC_AUT_ARRAY_FULL = 8721              # power search data array is filled
GRC_AUT_NO_DATA = 8722                 # no data available
GRC_KDM_NOT_AVAILABLE = 12544          # KDM device is not available.
GRC_FTR_FILEACCESS = 13056             # File access error
GRC_FTR_WRONGFILEBLOCKNUMBER = 13057   # block number was not the expected one
GRC_FTR_NOTENOUGHSPACE = 13058         # not enough space on device to proceed uploading
GRC_FTR_INVALIDINPUT = 13059           # Rename of file failed.
GRC_FTR_MISSINGSETUP = 13060           # invalid parameter as input

MESSAGES = {0: "Function successfully completed.",
            1: "Unknown error, result unspecified.",
            2: "Invalid parameter detected. Result unspecified.",
            3: "Invalid result.",
            4: "Fatal error.",
            5: "Not implemented yet.",
            6: "Function execution timed out. Result unspecified.",
            7: "Parameter setup for subsystem is incomplete.",
            8: "Function execution has been aborted.",
            9: "Fatal error - not enough memory.",
            10: "Fatal error - subsystem not initialized.",
            12: "Subsystem is down.",
            13: "System busy/already in use of another process. Cannot execute function.",
            14: "Fatal error - hardware failure.",
            15: "Execution of application has been aborted (SHIFT-ESC).",
            16: "Operation aborted - insufficient power supply level.",
            17: "Invalid version of file, ...",
            18: "Battery empty",
            20: "no event pending.",
            21: "out of temperature range",
            22: "instrument tilting out of range",
            23: "communication error",
            24: "GRC_TYPE Input 'do no action'",
            25: "Instr. run into the sleep mode",
            26: "Function not successfully completed.",
            27: "Not available",
            28: "Overflow error",
            29: "System or subsystem has been stopped",
            257: "Angles and Inclinations not valid",
            258: "inclinations not valid",
            259: "value accuracies not reached",
            260: "angle-accuracies not reached",
            261: "inclination accuracies not reached",
            266: "no write access allowed",
            267: "value out of range",
            268: "function aborted due to interrupt",
            269: "hz moved during incline measurement",
            270: "troubles with operation system",
            271: "overflow at parameter values",
            272: "too less peaks",
            273: "reading timeout",
            274: "too many exposures wanted",
            275: "picture height out of range",
            276: "positive exposure dynamic overflow",
            277: "negative exposure dynamic overflow",
            278: "exposure time overflow",
            279: "picture underexposured",
            280: "picture overexposured",
            300: "too many peaks detected",
            301: "too less peaks detected",
            302: "peak too slim",
            303: "peak to wide",
            304: "bad peak difference",
            305: "too less peak amplitude",
            306: "inhomogeneous peak amplitudes",
            307: "no peak decoding possible",
            308: "peak decoding not stable",
            309: "too less valid finepeaks",
            512: "ATR-System is not ready.",
            513: "Result isn't available yet.",
            514: "Several Targets detected.",
            515: "Spot is too big for analyse.",
            516: "Background is too bright.",
            517: "No targets detected.",
            518: "Accuracy worse than asked for.",
            519: "Spot is on the edge of the sensing area.",
            522: "Blooming or spot on edge detected.",
            523: "ATR isn't in a continuous mode.",
            524: "Not the spot of the own target illuminator.",
            525: "Communication error to sensor (ATR).",
            526: "Received Arguments cannot be decoded",
            527: "No Spot detected in Hz-direction.",
            528: "No Spot detected in V-direction.",
            529: "Strange light in Hz-direction.",
            530: "Strange light in V-direction.",
            531: "On multiple ATA_SLDR_OpenTransfer.",
            532: "No ATA_SLDR_OpenTransfer happened.",
            533: "Unexpected data format received.",
            534: "Checksum error in transmitted data.",
            535: "Address out of valid range.",
            536: "Firmware file has invalid format.",
            537: "Current (loaded) firmware doesn't support upload.",
            538: "PS-System is not ready.",
            539: "ATR system error",
            769: "Fatal EDM sensor error. See for the exact reason the original EDM sensor error number. In the most cases a service problem.",
            770: "Invalid command or unknown command, see command syntax.",
            771: "Boomerang error.",
            772: "Received signal to low, prism to far away, or natural barrier, bad environment, etc.",
            773: "obsolete",
            774: "Received signal to strong, prism to near, stranger light effect.",
            775: "Timeout, measuring time exceeded (signal too weak, beam interrupted,..)",
            776: "to much turbulences or distractions",
            777: "filter motor defective",
            778: "Device like EGL, DL is not installed.",
            779: "Search result invalid. For the exact explanation, see in the description of the called function.",
            780: "Communication ok, but an error reported from the EDM sensor.",
            781: "No service password is set.",
            782: "Communication ok, but an unexpected answer received.",
            783: "Data send error, sending buffer is full.",
            784: "Data receive error, like parity buffer overflow.",
            785: "Internal EDM subsystem error.",
            786: "Sensor is working already, abort current measuring first.",
            787: "No measurement activity started.",
            788: "Calculated checksum, resp. received data wrong (only in binary communication mode possible).",
            789: "During start up or shut down phase an error occured. It is saved in the DEL buffer.",
            790: "Red laser not available on this sensor HW.",
            791: "Measurement will be aborted (will be used for the laser security)",
            798: "Multiple OpenTransfer calls.",
            799: "No open transfer happened.",
            800: "Unexpected data format received.",
            801: "Checksum error in transmitted data.",
            802: "Address out of valid range.",
            803: "Firmware file has invalid format.",
            804: "Current (loaded) firmware doesn't support upload.",
            808: "Undocumented error from the EDM sensor, should not occur.",
            818: "Out of distance range (dist too small or large)",
            819: "Signal to noise ratio too small",
            820: "Noise to high",
            821: "Password is not set",
            822: "Elapsed time between prepare und start fast measurement for ATR to long",
            823: "Possibly more than one target (also a sensor error)",
            1283: "Warning: measurement without full correction",
            1284: "Info: accuracy can not be guarantee",
            1285: "Warning: only angle measurement valid",
            1288: "Warning: only angle measurement valid but without full correction",
            1289: "Info: only angle measurement valid but accuracy can not be guarantee",
            1290: "Error: no angle measurement",
            1291: "Error: wrong setting of PPM or MM on EDM",
            1292: "Error: distance measurement not done (no aim, etc.)",
            1293: "Error: system is busy (no measurement done)",
            1294: "Error: no signal on EDM (only in signal mode)",
            2305: "Loading process already opened",
            2306: "Transfer not opened",
            2307: "Unknown character set",
            2308: "Display module not present",
            2309: "Character set already exists",
            2310: "Character set cannot be deleted",
            2311: "Memory cannot be allocated",
            2312: "Character set still used",
            2313: "Charset cannot be deleted or is protected",
            2314: "Attempt to copy a character block outside the allocated memory",
            2315: "Error during release of allocated memory",
            2316: "Number of bytes specified in header does not match the bytes read",
            2317: "Allocated memory could not be released",
            2318: "Max. number of character sets already loaded",
            2319: "Layer cannot be deleted",
            2320: "Required layer does not exist",
            2321: "Layer length exceeds maximum",
            3072: "Initiate Extended Runtime Operation (ERO).",
            3073: "Cannot encode arguments in client.",
            3074: "Cannot decode results in client.",
            3075: "Hardware error while sending.",
            3076: "Hardware error while receiving.",
            3077: "Request timed out.",
            3078: "Packet format error.",
            3079: "Version mismatch between client and server.",
            3080: "Cannot decode arguments in server.",
            3081: "Unknown RPC, procedure ID invalid.",
            3082: "Cannot encode results in server.",
            3083: "Unspecified generic system error.",
            3085: "Unspecified error.",
            3086: "Binary protocol not available.",
            3087: "Call interrupted.",
            3090: "Protocol needs 8bit encoded characters.",
            3093: "TRANSACTIONS ID mismatch error.",
            3094: "Protocol not recognizable.",
            3095: "(WIN) Invalid port address.",
            3099: "ERO is terminating.",
            3100: "Internal error: data buffer overflow.",
            3101: "Invalid checksum on server side received.",
            3102: "Invalid checksum on client side received.",
            3103: "(WIN) Port not available.",
            3104: "(WIN) Port not opened.",
            3105: "(WIN) Unable to find TPS.",
            3106: "Extended Runtime Operation could not be started.",
            3107: "Att to send cons reqs",
            3108: "TPS has gone to sleep. Wait and try again.",
            3109: "TPS has shut down. Wait and try again.",
            8704: "Position not reached",
            8705: "Positioning not possible due to mounted EDM",
            8706: "Angle measurement error",
            8707: "Motorisation error",
            8708: "Position not exactly reached",
            8709: "Deviation measurement error",
            8710: "No target detected",
            8711: "Multiple target detected",
            8712: "Bad environment conditions",
            8713: "Error in target acquisition",
            8714: "Target acquisition not enabled",
            8715: "ATR-Calibration failed",
            8716: "Target position not exactly reached",
            8717: "Info: dist. measurement has been started",
            8718: "external Supply voltage is too high",
            8719: "int. or ext. Supply voltage is too low",
            8720: "working area not set",
            8721: "power search data array is filled",
            8722: "no data available",
            12544: "KDM device is not available.",
            13056: "File access error",
            13057: "block number was not the expected one",
            13058: "not enough space on device to proceed uploading",
            13059: "Rename of file failed.",
            13060: "invalid parameter as input",
            }


CODES = {0: "GRC_OK",
         1: "GRC_UNDEFINED",
         2: "GRC_IVPARAM",
         3: "GRC_IVRESULT",
         4: "GRC_FATAL",
         5: "GRC_NOT_IMPL",
         6: "GRC_TIME_OUT",
         7: "GRC_SET_INCOMPL",
         8: "GRC_ABORT",
         9: "GRC_NOMEMORY",
         10: "GRC_NOTINIT",
         12: "GRC_SHUT_DOWN",
         13: "GRC_SYSBUSY",
         14: "GRC_HWFAILURE",
         15: "GRC_ABORT_APPL",
         16: "GRC_LOW_POWER",
         17: "GRC_IVVERSION",
         18: "GRC_BATT_EMPTY",
         20: "GRC_NO_EVENT",
         21: "GRC_OUT_OF_TEMP",
         22: "GRC_INSTRUMENT_TILT",
         23: "GRC_COM_SETTING",
         24: "GRC_NO_ACTION",
         25: "GRC_SLEEP_MODE",
         26: "GRC_NOTOK",
         27: "GRC_NA",
         28: "GRC_OVERFLOW",
         29: "GRC_STOPPED",
         257: "GRC_ANG_ERROR",
         258: "GRC_ANG_INCL_ERROR",
         259: "GRC_ANG_BAD_ACC",
         260: "GRC_ANG_BAD_ANGLE_ACC",
         261: "GRC_ANG_BAD_INCLIN_ACC",
         266: "GRC_ANG_WRITE_PROTECTED",
         267: "GRC_ANG_OUT_OF_RANGE",
         268: "GRC_ANG_IR_OCCURED",
         269: "GRC_ANG_HZ_MOVED",
         270: "GRC_ANG_OS_ERROR",
         271: "GRC_ANG_DATA_ERROR",
         272: "GRC_ANG_PEAK_CNT_UFL",
         273: "GRC_ANG_TIME_OUT",
         274: "GRC_ANG_TOO_MANY_EXPOS",
         275: "GRC_ANG_PIX_CTRL_ERR",
         276: "GRC_ANG_MAX_POS_SKIP",
         277: "GRC_ANG_MAX_NEG_SKIP",
         278: "GRC_ANG_EXP_LIMIT",
         279: "GRC_ANG_UNDER_EXPOSURE",
         280: "GRC_ANG_OVER_EXPOSURE",
         300: "GRC_ANG_TMANY_PEAKS",
         301: "GRC_ANG_TLESS_PEAKS",
         302: "GRC_ANG_PEAK_TOO_SLIM",
         303: "GRC_ANG_PEAK_TOO_WIDE",
         304: "GRC_ANG_BAD_PEAKDIFF",
         305: "GRC_ANG_UNDER_EXP_PICT",
         306: "GRC_ANG_PEAKS_INHOMOGEN",
         307: "GRC_ANG_NO_DECOD_POSS",
         308: "GRC_ANG_UNSTABLE_DECOD",
         309: "GRC_ANG_TLESS_FPEAKS",
         512: "GRC_ATA_NOT_READY",
         513: "GRC_ATA_NO_RESULT",
         514: "GRC_ATA_SEVERAL_TARGETS",
         515: "GRC_ATA_BIG_SPOT",
         516: "GRC_ATA_BACKGROUND",
         517: "GRC_ATA_NO_TARGETS",
         518: "GRC_ATA_NOT_ACCURAT",
         519: "GRC_ATA_SPOT_ON_EDGE",
         522: "GRC_ATA_BLOOMING",
         523: "GRC_ATA_NOT_BUSY",
         524: "GRC_ATA_STRANGE_LIGHT",
         525: "GRC_ATA_V24_FAIL",
         526: "GRC_ATA_DECODE_ERROR",
         527: "GRC_ATA_HZ_FAIL",
         528: "GRC_ATA_V_FAIL",
         529: "GRC_ATA_HZ_STRANGE_L",
         530: "GRC_ATA_V_STRANGE_L",
         531: "GRC_ATA_SLDR_TRANSFER_PENDING",
         532: "GRC_ATA_SLDR_TRANSFER_ILLEGAL",
         533: "GRC_ATA_SLDR_DATA_ERROR",
         534: "GRC_ATA_SLDR_CHK_SUM_ERROR",
         535: "GRC_ATA_SLDR_ADDRESS_ERROR",
         536: "GRC_ATA_SLDR_INV_LOADFILE",
         537: "GRC_ATA_SLDR_UNSUPPORTED",
         538: "GRC_ATA_PS_NOT_READY",
         539: "GRC_ATA_ATR_SYSTEM_ERR",
         769: "GRC_EDM_SYSTEM_ERR",
         770: "GRC_EDM_INVALID_COMMAND",
         771: "GRC_EDM_BOOM_ERR",
         772: "GRC_EDM_SIGN_LOW_ERR",
         773: "GRC_EDM_DIL_ERR",
         774: "GRC_EDM_SIGN_HIGH_ERR",
         775: "GRC_EDM_TIMEOUT",
         776: "GRC_EDM_FLUKT_ERR",
         777: "GRC_EDM_FMOT_ERR",
         778: "GRC_EDM_DEV_NOT_INSTALLED",
         779: "GRC_EDM_NOT_FOUND",
         780: "GRC_EDM_ERROR_RECEIVED",
         781: "GRC_EDM_MISSING_SRVPWD",
         782: "GRC_EDM_INVALID_ANSWER",
         783: "GRC_EDM_SEND_ERR",
         784: "GRC_EDM_RECEIVE_ERR",
         785: "GRC_EDM_INTERNAL_ERR",
         786: "GRC_EDM_BUSY",
         787: "GRC_EDM_NO_MEASACTIVITY",
         788: "GRC_EDM_CHKSUM_ERR",
         789: "GRC_EDM_INIT_OR_STOP_ERR",
         790: "GRC_EDM_SRL_NOT_AVAILABLE",
         791: "GRC_EDM_MEAS_ABORTED",
         798: "GRC_EDM_SLDR_TRANSFER_PENDING",
         799: "GRC_EDM_SLDR_TRANSFER_ILLEGAL",
         800: "GRC_EDM_SLDR_DATA_ERROR",
         801: "GRC_EDM_SLDR_CHK_SUM_ERROR",
         802: "GRC_EDM_SLDR_ADDR_ERROR",
         803: "GRC_EDM_SLDR_INV_LOADFILE",
         804: "GRC_EDM_SLDR_UNSUPPORTED",
         808: "GRC_EDM_UNKNOW_ERR",
         818: "GRC_EDM_DISTRANGE_ERR",
         819: "GRC_EDM_SIGNTONOISE_ERR",
         820: "GRC_EDM_NOISEHIGH_ERR",
         821: "GRC_EDM_PWD_NOTSET",
         822: "GRC_EDM_ACTION_NO_MORE_VALID",
         823: "GRC_EDM_MULTRG_ERR",
         1283: "GRC_TMC_NO_FULL_CORRECTION",
         1284: "GRC_TMC_ACCURACY_GUARANTEE",
         1285: "GRC_TMC_ANGLE_OK",
         1288: "GRC_TMC_ANGLE_NOT_FULL_CORR",
         1289: "GRC_TMC_ANGLE_NO_ACC_GUARANTY",
         1290: "GRC_TMC_ANGLE_ERROR",
         1291: "GRC_TMC_DIST_PPM",
         1292: "GRC_TMC_DIST_ERROR",
         1293: "GRC_TMC_BUSY",
         1294: "GRC_TMC_SIGNAL_ERROR",
         2305: "GRC_BMM_XFER_PENDING",
         2306: "GRC_BMM_NO_XFER_OPEN",
         2307: "GRC_BMM_UNKNOWN_CHARSET",
         2308: "GRC_BMM_NOT_INSTALLED",
         2309: "GRC_BMM_ALREADY_EXIST",
         2310: "GRC_BMM_CANT_DELETE",
         2311: "GRC_BMM_MEM_ERROR",
         2312: "GRC_BMM_CHARSET_USED",
         2313: "GRC_BMM_CHARSET_SAVED",
         2314: "GRC_BMM_INVALID_ADR",
         2315: "GRC_BMM_CANCELANDADR_ERROR",
         2316: "GRC_BMM_INVALID_SIZE",
         2317: "GRC_BMM_CANCELANDINVSIZE_ERROR",
         2318: "GRC_BMM_ALL_GROUP_OCC",
         2319: "GRC_BMM_CANT_DEL_LAYERS",
         2320: "GRC_BMM_UNKNOWN_LAYER",
         2321: "GRC_BMM_INVALID_LAYERLEN",
         3072: "GRC_COM_ERO",
         3073: "GRC_COM_CANT_ENCODE",
         3074: "GRC_COM_CANT_DECODE",
         3075: "GRC_COM_CANT_SEND",
         3076: "GRC_COM_CANT_RECV",
         3077: "GRC_COM_TIMEDOUT",
         3078: "GRC_COM_WRONG_FORMAT",
         3079: "GRC_COM_VER_MISMATCH",
         3080: "GRC_COM_CANT_DECODE_REQ",
         3081: "GRC_COM_PROC_UNAVAIL",
         3082: "GRC_COM_CANT_ENCODE_REP",
         3083: "GRC_COM_SYSTEM_ERR",
         3085: "GRC_COM_FAILED",
         3086: "GRC_COM_NO_BINARY",
         3087: "GRC_COM_INTR",
         3090: "GRC_COM_REQUIRES_8DBITS",
         3093: "GRC_COM_TR_ID_MISMATCH",
         3094: "GRC_COM_NOT_GEOCOM",
         3095: "GRC_COM_UNKNOWN_PORT",
         3099: "GRC_COM_ERO_END",
         3100: "GRC_COM_OVERRUN",
         3101: "GRC_COM_SRVR_RX_CHECKSUM_ERRR",
         3102: "GRC_COM_CLNT_RX_CHECKSUM_ERRR",
         3103: "GRC_COM_PORT_NOT_AVAILABLE",
         3104: "GRC_COM_PORT_NOT_OPEN",
         3105: "GRC_COM_NO_PARTNER",
         3106: "GRC_COM_ERO_NOT_STARTED",
         3107: "GRC_COM_CONS_REQ",
         3108: "GRC_COM_SRVR_IS_SLEEPING",
         3109: "GRC_COM_SRVR_IS_OFF",
         8704: "GRC_AUT_TIMEOUT",
         8705: "GRC_AUT_DETENT_ERROR",
         8706: "GRC_AUT_ANGLE_ERROR",
         8707: "GRC_AUT_MOTOR_ERROR",
         8708: "GRC_AUT_INCACC",
         8709: "GRC_AUT_DEV_ERROR",
         8710: "GRC_AUT_NO_TARGET",
         8711: "GRC_AUT_MULTIPLE_TARGETS",
         8712: "GRC_AUT_BAD_ENVIRONMENT",
         8713: "GRC_AUT_DETECTOR_ERROR",
         8714: "GRC_AUT_NOT_ENABLED",
         8715: "GRC_AUT_CALACC",
         8716: "GRC_AUT_ACCURACY",
         8717: "GRC_AUT_DIST_STARTED",
         8718: "GRC_AUT_SUPPLY_TOO_HIGH",
         8719: "GRC_AUT_SUPPLY_TOO_LOW",
         8720: "GRC_AUT_NO_WORKING_AREA",
         8721: "GRC_AUT_ARRAY_FULL",
         8722: "GRC_AUT_NO_DATA",
         12544: "GRC_KDM_NOT_AVAILABLE",
         13056: "GRC_FTR_FILEACCESS",
         13057: "GRC_FTR_WRONGFILEBLOCKNUMBER",
         13058: "GRC_FTR_NOTENOUGHSPACE",
         13059: "GRC_FTR_INVALIDINPUT",
         13060: "GRC_FTR_MISSINGSETUP",
         }

BMM_BeepAlarm = 11004           # Page: 46
BMM_BeepNormal = 11003          # Page: 47
COM_GetDoublePrecision = 108    # Page: 21
COM_GetSWVersion = 110          # Page: 49
COM_NullProc = 0                # Page: 52
COM_SetDoublePrecision = 107    # Page: 22
COM_SwitchOffTPS = 112          # Page: 51
COM_SwitchOnTPS = 111           # Page: 50
CSV_GetDateTime = 5008          # Page: 59
CSV_GetDeviceConfig = 5035      # Page: 57, 58
CSV_GetInstrumentName = 5004    # Page: 56
CSV_GetInstrumentNo = 5003      # Page: 55
CSV_GetIntTemp = 5011           # Page: 63
CSV_GetSWVersion = 5034         # Page: 61
CSV_SetDateTime = 5007          # Page: 60
EDM_GetEglIntensity = 1058      # Page:  39, 40, 41, 42, 43, 44, 66
EDM_Laserpointer = 1004         # Page: 65
EDM_SetEglIntensity = 1059      # Page: 67
SUP_GetConfig = 14001           # Page: 69
SUP_SetConfig = 14002           # Page: 70
TMC_DoMeasure = 2008            # Page: 86
TMC_GetAngle1 = 2003            # Page: 79
TMC_GetAngle5 = 2107            # Page: 81
TMC_GetAngSwitch = 2014         # Page: 108
TMC_GetAtmCorr = 2029           # Page: 91
TMC_GetCoordinate = 2082        # Page: 75
TMC_GetEdmMode = 2021           # Page: 111
TMC_GetFace = 2026              # Page: 106
TMC_GetHeight = 2011            # Page: 89
TMC_GetInclineSwitch = 2007     # Page: 109
TMC_GetPrismCorr = 2023         # Page: 95
TMC_GetRefractiveCorr = 2031    # Page: 96
TMC_GetRefractiveMethod = 2091  # Page: 98
TMC_GetSignal = 2022            # Page: 107
TMC_GetSimpleCoord = 2116       # Page: 113
TMC_GetSimpleMea = 2108         # Page: 77
TMC_GetSlopeDistCorr = 2126     # Page: 118
TMC_GetStation = 2009           # Page: 100
TMC_IfDataAzeCorrError = 2114   # Page: 115
TMC_IfDataIncCorrError = 2115   # Page: 116
TMC_QuickDist = 2117            # Page: 83
TMC_SetAngSwitch = 2016         # Page: 117
TMC_SetAtmCorr = 2028           # Page: 92
TMC_SetEdmMode = 2020           # Page: 112
TMC_SetHandDist = 2019          # Page: 87
TMC_SetHeight = 2012            # Page: 90
TMC_SetInclineSwitch = 2006     # Page: 110
TMC_SetOrientation = 2113       # Page: 93
TMC_SetRefractiveCorr = 2030    # Page: 97
TMC_SetRefractiveMethod = 2090  # Page: 99
TMC_SetStation = 2010           # Page: 101
CRLF = "\r\n"
