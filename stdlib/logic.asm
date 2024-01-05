__logic_equal:
    jr z, __logic_true
__logic_false:
    xor a
    ret
__logic_not_equal:
    jr nz, __logic_true
    xor a
    ret
__logic_equal_less:
    jr z, __logic_true
__logic_less:
    jr c, __logic_true
    xor a
    ret
__logic_greater:
    jr z, __logic_false
__logic_equal_greater:
    jr c, __logic_false
__logic_true:
    ld a, 1
    ret
