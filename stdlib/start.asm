std_start:
    call __init
    call _function_main
    di
    halt
    db $DD ; ill instruction, will hard-halt on hardware, crash/abort various emulators
