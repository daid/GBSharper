std_start:
    call __init
    call _main
    di
    halt
    db $DD ; ill instruction, will hard-halt on hardware, crash/abort various emulators
