ALWAYS modify the environment variable PATH, use the following command (for C shell)

	setenv PATH $PATH":/u/d/lisiyun/ECE353/bin"
or
	setenv PATH $PATH":/share/copy/ece353s/blitz/bin"

Copy Blitz binaries from: 
	/share/copy/ece353s/blitz/bin

Copy LAB FILES from:
	/share/copy/ece353s/lab1

Not required but good to know: 
	Blitz source code: /share/copy/ece353s/blitz/src

BLITZ tool set: 
	kpl, asm, lddd, blitz, diskUtil, 
	dumpObj, hexdump, check, endian

Assembly file proc:
	asm Hello.s
	lddd Hello.o -o Hello
	blitz -g Hello

Use KPL:
	kpl -unsafe System
	asm System.s
	kpl HelloWorld
	asm HelloWorld.s
	asm Runtime.s
	lddd Runtime.o System.o HelloWorld.o -o HelloWorld
	blitz -g HelloWorld

Changes to System.h only require re-linking to produce the executable (lddd)
For other changes to the header files used by an executable, must re-compile with "make"

Emulator Commands: 
	quit(q), help(h), go(g), step(s), t(KPL one by one), 
	reset, info(i), stack(st), frame(fr), up, down

"DISK" file: must have, otherwise emulator prints a warning.
