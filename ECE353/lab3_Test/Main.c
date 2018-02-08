code Main

  -- OS Class: Project 3
  --
  -- <PUT YOUR NAME HERE>
  --

  -- This package contains the following:
  --     Dining Philospohers
-----------------------------  Main  ---------------------------------

  function main ()
      InitializeScheduler ()
      -- DiningPhilosophers ()
      -- ThreadFinish()
      
      -- SleepingBarber()
      -- ThreadFinish()
      
      DiningPhilosophers ()
      ThreadFinish()
      -- FatalError ("Need to implement")
    endFunction




-----------------------------  Dining Philosophers  ----------------------------

  -- This code is an implementation of the Dining Philosophers problem.  Each
  -- philosopher is simulated with a thread.  Each philosopher thinks for a while
  -- and then wants to eat.  Before eating, he must pick up both his forks.
  -- After eating, he puts down his forks.  Each fork is shared between
  -- two philosophers and there are 5 philosophers and 5 forks arranged in a
  -- circle.
  --
  -- Since the forks are shared, access to them is controlled by a monitor
  -- called "ForkMonitor".  The monitor is an object with two "entry" methods:
  --     PickupForks (phil)
  --     PutDownForks (phil)
  -- The philsophers are numbered 0 to 4 and each of these methods is passed an 
  -- integer indicating which philospher wants to pickup (or put down) the forks.
  -- The call to "PickUpForks" will wait until both of his forks are
  -- available.  The call to "PutDownForks" will never wait and may also
  -- wake up threads (i.e., philosophers) who are waiting.
  --
  -- Each philospher is in exactly one state: HUNGRY, EATING, or THINKING.  Each
  -- time a philosopher's state changes, a line of output is printed.  The 
  -- output is organized so that each philosopher has column of output with the
  -- following code letters:
  --           E    --  eating
  --           .    --  thinking
  --         blank  --  hungry (i.e., waiting for forks)
  -- By reading down a column, you can see the history of a philosopher.
  --
  -- The forks are not modeled explicitly.  A fork is only picked up
  -- by a philosopher if he can pick up both forks at the same time and begin
  -- eating.  To know whether a fork is available, it is sufficient to simply
  -- look at the status's of the two adjacent philosophers.  (Another way to 
  -- state the problem is to forget about the forks altogether and stipulate 
  -- that a philosopher may only eat when his two neighbors are not eating.)

  enum HUNGRY, EATING, THINKING
  var
    mon: ForkMonitor
    philospher: array [5] of Thread = new array of Thread {5 of new Thread }

  function DiningPhilosophers ()

      print ("Plato\n")
      print ("    Sartre\n")
      print ("        Kant\n")
      print ("            Nietzsche\n")
      print ("                Aristotle\n")

      mon = new ForkMonitor
      mon.Init ()
      mon.PrintAllStatus ()

      philospher[0].Init ("Plato")
      philospher[0].Fork (PhilosphizeAndEat, 0)

      philospher[1].Init ("Sartre")
      philospher[1].Fork (PhilosphizeAndEat, 1)

      philospher[2].Init ("Kant")
      philospher[2].Fork (PhilosphizeAndEat, 2)

      philospher[3].Init ("Nietzsche")
      philospher[3].Fork (PhilosphizeAndEat, 3)

      philospher[4].Init ("Aristotle")
      philospher[4].Fork (PhilosphizeAndEat, 4)

     endFunction

  function PhilosphizeAndEat (p: int)
    -- The parameter "p" identifies which philosopher this is.
    -- In a loop, he will think, acquire his forks, eat, and
    -- put down his forks.
      var
        i: int
      for i = 1 to 7
        -- Now he is thinking
        mon.PickupForks (p)
        -- Now he is eating
        mon.PutDownForks (p)
      endFor
    endFunction

  class ForkMonitor
    superclass Object
    fields
      status: array [5] of int -- For each philosopher: HUNGRY, EATING, or THINKING
      mutex: Mutex
      condition: array [5] of Condition
    methods
      Init ()
      PickupForks (p: int)
      PutDownForks (p: int)
      PrintAllStatus ()
  endClass

  behavior ForkMonitor

    method Init ()
      -- Initialize so that all philosophers are THINKING.
      -- ...unimplemented...
      var i: int
      status = new array of int { 5 of THINKING }
      condition = new array [5] of Condition { 5 of new Condition }
      for i = 0 to 4
        condition[i].Init ()
      endFor
      mutex = new Mutex
      mutex.Init ()
      endMethod

    method PickupForks (p: int)
      -- This method is called when philosopher 'p' wants to eat.
      -- ...unimplemented...
      mutex.Lock()
      status [p] = HUNGRY
      self.PrintAllStatus ()
      while status[(p+4)%5]==EATING || status[(p+1)%5]==EATING
        condition[p].Wait(&mutex)
      endWhile
      status[p] = EATING
      self.PrintAllStatus()
      mutex.Unlock()
      endMethod

    method PutDownForks (p: int)
      -- This method is called when the philosopher 'p' is done eating.
      -- ...unimplemented...
      mutex.Lock()
      status[p] = THINKING
      self.PrintAllStatus()
      if status[(p+4)%5]==HUNGRY
        condition[(p+4)%5].Signal(&mutex)
      endIf
      if status[(p+1)%5]==HUNGRY
        condition[(p+1)%5].Signal(&mutex)
      endIf
      mutex.Unlock()
      endMethod

    method PrintAllStatus ()
      -- Print a single line showing the status of all philosophers.
      --      '.' means thinking
      --      ' ' means hungry
      --      'E' means eating
      -- Note that this method is internal to the monitor.  Thus, when
      -- it is called, the monitor lock will already have been acquired
      -- by the thread.  Therefore, this method can never be re-entered,
      -- since only one thread at a time may execute within the monitor.
      -- Consequently, printing is safe.  This method calls the "print"
      -- routine several times to print a single line, but these will all
      -- happen without interuption.
        var
          p: int
        for p = 0 to 4
          switch status [p]
            case HUNGRY:
              print ("    ")
              break
            case EATING:
              print ("E   ")
              break
            case THINKING:
              print (".   ")
              break
          endSwitch
        endFor
        nl ()
      endMethod

  endBehavior
  
-----------------------------  Sleeping Barber  ----------------------------

  const
    CHAIRS = 5
    CUSTOMER_NUM = 10
    
  var
    customers: array [10] of Thread = new array of Thread {10 of new Thread }
    barber: Thread
    waiting: int
    access_lock: Mutex
    customers_sem : Semaphore
    customers_done_sem : Semaphore
    barber_sem: Semaphore
    barber_done_sem: Semaphore

  function SleepingBarber ()

      waiting = 0
      
      customers_sem = new Semaphore
      customers_sem.Init(0)
      
      customers_done_sem = new Semaphore
      customers_done_sem.Init(0)
      
      barber_sem = new Semaphore
      barber_sem.Init(0)
      
      barber_done_sem = new Semaphore
      barber_done_sem.Init(0)
      
      access_lock = new Mutex
      access_lock.Init()
      
      PrintHead()
      barber = new Thread
      barber.Init("Barber")
      barber.Fork (barber_fn, 0)
      
      --print ("Customer 0 creating!\n")
      customers[0].Init ("0")
      customers[0].Fork (customer_fn, 2)
      
      --print ("Customer 1 creating!\n")
      customers[1].Init ("1")
      customers[1].Fork (customer_fn, 2)
      
      --print ("Customer 2 creating!\n")
      customers[2].Init ("2")
      customers[2].Fork (customer_fn, 2)
      
      --print ("Customer 3 creating!\n")
      customers[3].Init ("3")
      customers[3].Fork (customer_fn, 2)
      
      --print ("Customer 4 creating!\n")
      customers[4].Init ("4")
      customers[4].Fork (customer_fn, 2)
      
      --print ("Customer 5 creating!\n")
      customers[5].Init ("5")
      customers[5].Fork (customer_fn, 2)
      
      --print ("Customer 6 creating!\n")
      customers[6].Init ("6")
      customers[6].Fork (customer_fn, 2)
      
      --print ("Customer 7 creating!\n")
      customers[7].Init ("7")
      customers[7].Fork (customer_fn, 2)
      
      --print ("Customer 8 creating!\n")
      customers[8].Init ("8")
      customers[8].Fork (customer_fn, 2)
      
      --print ("Customer 9 creating!\n")
      customers[9].Init ("9")
      customers[9].Fork (customer_fn, 2)

     endFunction

  function barber_fn (not_used: int)
      while true
        customers_sem.Down()
        access_lock.Lock()
        waiting = waiting -1
        access_lock.Unlock()
        PrintBarberStart()
        barber_sem.Up()
        currentThread.Yield() -- cut_hair()
        customers_done_sem.Down()
        PrintBarberEnd()
        barber_done_sem.Up()
      endWhile
    endFunction
    
  function customer_fn (cut_num:int)
      var
        i: int
      for i = 1 to cut_num
        access_lock.Lock()
        PrintCustomerState(charToInt(currentThread.name[0]) - charToInt('0'), "E")
        if waiting < CHAIRS
          waiting = waiting +1
          PrintCustomerState(charToInt(currentThread.name[0]) - charToInt('0'), "S")
          access_lock.Unlock()
          customers_sem.Up()
          barber_sem.Down()
          PrintCustomerState(charToInt(currentThread.name[0]) - charToInt('0'), "B")
          currentThread.Yield() -- get_haircut()
          PrintCustomerState(charToInt(currentThread.name[0]) - charToInt('0'), "F")
          customers_done_sem.Up()
          barber_done_sem.Down()
        else
          access_lock.Unlock()
        endIf
        PrintCustomerState(charToInt(currentThread.name[0]) - charToInt('0'), "L")
      endFor
    endFunction
  
  function PrintHead ()
    var i: int
    print("        Barber")
    for i = i to CUSTOMER_NUM-1
      print("  ")
      printInt (i)
    endFor
    print("\n")
  endFunction
  
  function PrintBarberStart ()
      var
        oldStatus: int
      oldStatus = SetInterruptsTo (DISABLED)
      print ("        start\n")
      oldStatus = SetInterruptsTo (oldStatus)
    endFunction
  
  function PrintBarberEnd ()
      var
        oldStatus: int
      oldStatus = SetInterruptsTo (DISABLED)
      print ("        end\n")
      oldStatus = SetInterruptsTo (oldStatus)
    endFunction
    
  function PrintCustomerState(custn: int, custs: ptr to array of char)
      var
        oldStatus: int
        i: int
      oldStatus = SetInterruptsTo (DISABLED)
      for i = 1 to CHAIRS
        if i <= waiting
          print ("X")
        else
          print ("-")
        endIf
      endFor
      print ("           ")
      for i = 0 to CUSTOMER_NUM-1
        if i == custn
          print (custs)
          print ("  ")
        else
          print (" ")
          print ("  ")
        endIf
      endFor
      print ("\n")
      oldStatus = SetInterruptsTo (oldStatus)
    endFunction

-----------------------------  Gaming Parlor  ----------------------------
  const
    Backgammon = 4
    Risk = 5
    Monopoly = 2
    Pictionary = 1
  var
    gpmon: GPMonitor
    customer: array [5] of Thread = new array of Thread {5 of new Thread }

  function DiningPhilosophers ()

      gpmon = new GPMonitor
      gpmon.Init ()
      
      dice = 8

      customer[0].Init ("A")
      customer[0].Fork (PlayGame, Backgammon)

      customer[1].Init ("B")
      customer[1].Fork (PlayGame, Backgammon)

      customer[2].Init ("C")
      customer[2].Fork (PlayGame, Risk)

      customer[3].Init ("D")
      customer[3].Fork (PlayGame, Risk)

      customer[4].Init ("E")
      customer[4].Fork (PlayGame, Monopoly)
      
      customer[5].Init ("F")
      customer[5].Fork (PlayGame, Monopoly)

      customer[6].Init ("G")
      customer[6].Fork (PlayGame, Pictionary)

      customer[7].Init ("H")
      customer[7].Fork (PlayGame, Pictionary)

     endFunction

  function PlayGame (game: int)
      gpmon.Request(game)
      currentThread.Yield()
      gpmon.Return(game)
    endFunction

  class GPMonitor
    superclass Object
    fields
      dice: int
      mutex: Mutex
      condition: Condition
    methods
      Init ()
      Request (numberOfDice: int)
      Return (numberOfDice: int)
      ReturnPrint (num_dice: int)
      RequestPrint (num_dice: int)
      ProceedPrint (num_dice: int)
      AvailableDice()
  endClass

  behavior ForkMonitor

    method Init ()
      dice = 8
      condition = new Condition
      condition.Init ()
      mutex = new Mutex
      mutex.Init ()
      endMethod

    method Request (request_dice: int)
      mutex.Lock()
      RequestPrint(request_dice)
      while dice < request_dice
        condition.Wait(&mutex)
      endWhile
      dice = dice - request_dice
      ProceedPrint (request_dice)
      mutex.Unlock()
      endMethod

    method Return (return_dice: int)
      mutex.Lock()
      dice = dice+return_dice
      ReturnPrint (return_dice)
      condition.Broadcast(&mutex)
      mutex.Unlock()
      endMethod
    
    method ReturnPrint (num_dice: int)
      print(currentThread.name)
      print(" releases and adds back ")
      printInt(n)
      print ("\n")
      self.AvailableDice()
    endMethod
    
    method RequestPrint (num_dice: int)
      print(currentThread.name)
      print(" requests ")
      printInt(n)
      print ("\n")
      self.AvailableDice()
    endMethod
    
    method ProceedPrint (num_dice: int)
      print(currentThread.name)
      print(" proceeds with ")
      printInt(n)
      print ("\n")
      self.AvailableDice()
    endMethod
    
    method AvailableDice()
      print("---------------Number of dice now avail = ")
      printInt(dice)
      print ("\n")
    endMethod

  endBehavior

endCode
