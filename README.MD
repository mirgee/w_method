# W method
Program for derivation of characterization set given a description of corresponding finite state machine (FSM) using the W method.

Characterization set is a finite set of minimal and complete finite automaton input sequences which are guaranteed to distinguish 
the behavior of any pair of states in the FSM. This set can then be used as an effective test set for the FSM.

W method generates the characterization set from a sequence k-equivalent partitions. For details, see Adytia P. Marthur, "Foundations of Software Testing".

### How to run
If desired, enter custom input FSM filename (in CSV format) in `FSM.py` and run
 
 ``python2.7 FSM.py``.

The output consists of state cover, edge cover, equivalence partitions, characterization set, outputs for inputs from 
characterization set, derived test set, and inputs from characterization set which distinguishes individual FSM states.