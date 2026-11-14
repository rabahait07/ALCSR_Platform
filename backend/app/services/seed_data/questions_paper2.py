"""Multiple-choice questions for Paper 2 (Algorithms and Programming), keyed by spec code."""

from app.services.seed_data.types import SeedQuestion as Q

_GRADE_SELECTION = """\
if score >= 70 then
    grade = "A"
elseif score >= 50 then
    grade = "B"
else
    grade = "C"
endif"""

_COUNTING_LOOP = """\
count = 0
while count < 3
    count = count + 1
endwhile"""

_RECURSIVE_FUNCTION = """\
function calc(n)
    if n <= 1 then
        return 1
    else
        return n * calc(n - 1)
    endif
endfunction"""

_BY_VALUE_PROCEDURE = """\
procedure double(x:byVal)
    x = x * 2
endprocedure

num = 5
double(num)
print(num)"""

PAPER_2_QUESTIONS: dict[str, tuple[Q, ...]] = {
    # --- 2.1.1 Thinking abstractly ---------------------------------------------------------
    "2.1.1": (
        Q(
            "What is abstraction?",
            (
                "Removing unnecessary detail so that only the features relevant to the "
                "problem remain",
                "Breaking a problem down into smaller parts",
                "Writing a subroutine that calls itself",
                "Running several tasks at the same time",
            ),
            0,
            "Abstraction hides or removes detail that does not matter for the problem "
            "being solved, leaving a simpler model that is easier to understand and "
            "work with.",
        ),
        Q(
            "Which of these is an example of abstraction?",
            (
                "A photograph of a railway station",
                "A full-size replica of a train",
                "A map of a rail network showing only the stations and the lines that "
                "connect them",
                "A list of every passenger on a train",
            ),
            2,
            "A network map leaves out distances, the exact route of the track and the "
            "surrounding geography. It keeps only what a traveller needs: the stations "
            "and how they connect.",
        ),
        Q(
            "Why is abstraction needed when modelling a real-world system?",
            (
                "It guarantees that the program has no bugs",
                "It makes the model identical to reality",
                "It removes the need for testing",
                "It reduces complexity, so the solution is quicker to design and needs less "
                "memory and processing",
            ),
            3,
            "Reality contains far more detail than a program can or should handle. "
            "Leaving out what is irrelevant makes the problem solvable and the program "
            "smaller, faster and easier to write.",
        ),
    ),
    # --- 2.1.2 Thinking ahead --------------------------------------------------------------
    "2.1.2": (
        Q(
            "What is a precondition?",
            (
                "A value returned by a function",
                "A condition that must be true before a subroutine runs for it to work "
                "correctly",
                "A test carried out after the program has been written",
                "A comment at the top of a program",
            ),
            1,
            "A precondition is a requirement that must be met before a piece of code is "
            "run. For example, a binary search has the precondition that the list is "
            "sorted. Stating preconditions avoids repeating checks and makes subroutines "
            "easier to reuse.",
        ),
        Q(
            "What is caching?",
            (
                "Storing data that has been used in fast-access memory so that it can be "
                "retrieved quickly if it is needed again",
                "Deleting data that is no longer needed",
                "Splitting a problem into smaller parts",
                "Compressing files before they are sent",
            ),
            0,
            "Caching keeps data that is likely to be needed again where it can be reached "
            "quickly, such as web pages already visited. It saves time, but cached data "
            "can become out of date and takes up memory.",
        ),
        Q(
            "Which is an advantage of using reusable program components such as library "
            "subroutines?",
            (
                "They always run faster than code written specially for the task",
                "They never need updating",
                "They have already been written and tested, which saves development time",
                "They use no memory",
            ),
            2,
            "Reusable components have already been written, tested and documented, so "
            "using them shortens development and reduces errors. They may not fit a task "
            "exactly, however, and can include features that are not needed.",
        ),
    ),
    # --- 2.1.3 Thinking procedurally -------------------------------------------------------
    "2.1.3": (
        Q(
            "What is meant by decomposition (top-down design)?",
            (
                "Removing unnecessary detail from a problem",
                "Testing a program from the top of the code to the bottom",
                "Combining several small programs into one large program",
                "Breaking a problem into smaller sub-problems until each can be solved as a "
                "single task",
            ),
            3,
            "Decomposition splits a problem into sub-problems, and those into smaller "
            "ones again, until each is simple enough to be written as one subroutine. "
            "This is also known as stepwise refinement.",
        ),
        Q(
            "Which is a benefit of splitting a large program into sub-procedures?",
            (
                "The program does not need to be tested",
                "Different programmers can work on separate sub-procedures at the same time",
                "The program uses no memory",
                "The finished program cannot contain logic errors",
            ),
            1,
            "Sub-procedures can be written and tested independently by different members "
            "of a team, reused elsewhere, and maintained more easily because each one "
            "does a single job.",
        ),
        Q(
            "Why is it important to work out the order of the steps needed to solve a problem?",
            (
                "Some steps rely on the results of earlier steps, so carrying them out in "
                "the wrong order gives wrong results",
                "Steps always run faster in alphabetical order",
                "The order only matters in assembly language",
                "It reduces the number of variables needed",
            ),
            0,
            "Many steps depend on earlier ones: data must be input before it can be "
            "validated, and validated before it is processed. Identifying the order also "
            "shows which steps do not depend on each other and could be done concurrently.",
        ),
    ),
    # --- 2.1.4 Thinking logically ----------------------------------------------------------
    "2.1.4": (
        Q(
            "What is a decision point in a program?",
            (
                "The line where a variable is declared",
                "The end of a subroutine",
                "A place where the next step taken depends on whether a condition is true "
                "or false",
                "A comment explaining a calculation",
            ),
            2,
            "A decision point is where the flow of a program can branch. The path "
            "followed depends on a logical condition, as in an if statement or the "
            "condition that controls a loop.",
        ),
        Q(
            "The pseudocode shown is run with score equal to 50. What is the value of grade "
            "afterwards?",
            ('"A"', '"B"', '"C"', "grade is not given a value"),
            1,
            "The first condition, 50 >= 70, is false. The second, 50 >= 50, is true, so "
            'grade is set to "B" and the else branch is skipped.',
            code=_GRADE_SELECTION,
        ),
        Q(
            "How many times is the body of the loop shown executed?",
            ("It never stops", "2", "4", "3"),
            3,
            "count takes the values 0, 1 and 2 at the start of each pass and is "
            "increased by 1 every time. When count reaches 3 the condition count < 3 is "
            "false, so the body has run three times.",
            code=_COUNTING_LOOP,
        ),
    ),
    # --- 2.1.5 Thinking concurrently -------------------------------------------------------
    "2.1.5": (
        Q(
            "What is concurrent processing?",
            (
                "Several tasks are in progress at the same time, each being given slices of "
                "processor time",
                "One task must finish completely before the next begins",
                "A task is split into parts that always run in a fixed order",
                "Instructions are fetched before they are needed",
            ),
            0,
            "In concurrent processing more than one task is under way during the same "
            "period, with the processor switching between them. Parallel processing goes "
            "further and needs several processors or cores to run tasks at the same "
            "instant.",
        ),
        Q(
            "Which is a benefit of concurrent processing?",
            (
                "Programs become easier to write and test",
                "Other tasks can make progress while one task waits for input",
                "Deadlock can never occur",
                "Every task is guaranteed to finish sooner",
            ),
            1,
            "More work is completed in a given time because the processor is not idle "
            "while a task waits, for example for user input. The trade-off is that "
            "concurrent programs are harder to write and debug.",
        ),
        Q(
            "Two processes each hold a resource that the other needs, and neither can "
            "continue. What is this situation called?",
            ("Pipelining", "Caching", "Deadlock", "Backtracking"),
            2,
            "Deadlock happens when each process waits for a resource that the other has "
            "locked, so neither can go on. It is one of the risks of concurrent "
            "processing and of record locking in databases.",
        ),
    ),
    # --- 2.2.1 Programming techniques ------------------------------------------------------
    "2.2.1": (
        Q(
            "Which are the three basic programming constructs?",
            (
                "Sequence, selection and iteration",
                "Input, process and output",
                "Variables, constants and arrays",
                "Functions, procedures and parameters",
            ),
            0,
            "Any algorithm can be built from sequence (steps carried out in order), "
            "selection (choosing a path with a condition) and iteration (repeating "
            "steps in a loop).",
        ),
        Q(
            "The function shown is called with calc(4). What value is returned?",
            ("4", "10", "16", "24"),
            3,
            "calc(4) returns 4 * calc(3), calc(3) returns 3 * calc(2), calc(2) returns "
            "2 * calc(1) and calc(1) returns 1. The result is 4 * 3 * 2 * 1 = 24: the "
            "function calculates a factorial.",
            code=_RECURSIVE_FUNCTION,
        ),
        Q(
            "What must a recursive subroutine include so that it does not call itself forever?",
            (
                "A global variable",
                "A base case that will eventually be reached",
                "A for loop",
                "At least two parameters",
            ),
            1,
            "A recursive subroutine needs a base case, a condition under which it "
            "returns without calling itself, and each call must move closer to it. "
            "Without one the call stack keeps growing until a stack overflow occurs.",
        ),
        Q(
            "What is a local variable?",
            (
                "A variable that can be accessed from anywhere in the program",
                "A variable whose value can never change",
                "A variable that can only be accessed within the subroutine in which it is "
                "declared",
                "A variable stored on secondary storage",
            ),
            2,
            "A local variable exists only while its subroutine is running and cannot be "
            "seen outside it. This keeps subroutines self-contained and frees the memory "
            "when the subroutine ends.",
        ),
        Q(
            "Why is heavy use of global variables discouraged?",
            (
                "They cannot store numbers",
                "They can be changed from anywhere in the program, which makes errors hard "
                "to trace",
                "They are deleted every time a subroutine ends",
                "They can only be used once",
            ),
            1,
            "Because any part of the program can alter a global variable, an unexpected "
            "change is difficult to track down. Global variables also occupy memory for "
            "as long as the program runs and make subroutines harder to reuse.",
        ),
        Q(
            "What happens when a parameter is passed by reference?",
            (
                "A copy of the value is passed, so the original variable is unchanged",
                "The parameter becomes a constant",
                "The subroutine cannot use the parameter",
                "The address of the variable is passed, so changes made inside the "
                "subroutine affect the original",
            ),
            3,
            "Passing by reference gives the subroutine the memory address of the "
            "argument, so it works on the original variable. Passing by value gives it a "
            "copy, leaving the original untouched.",
        ),
        Q(
            "What is output when the pseudocode shown is run?",
            ("5", "10", "0", "An error message"),
            0,
            "x is passed by value, so the procedure receives a copy of num. Doubling the "
            "copy does not change num, which still holds 5 when it is printed.",
            code=_BY_VALUE_PROCEDURE,
        ),
        Q(
            "How does a function differ from a procedure?",
            (
                "A function cannot take parameters",
                "A function cannot be called more than once",
                "A function always returns a value",
                "A function must be recursive",
            ),
            2,
            "Both are named blocks of code that can take parameters. A function returns "
            "a value to the code that called it, so it can be used in an expression; a "
            "procedure does not return a value.",
        ),
        Q(
            "Which IDE feature pauses a program at a chosen line so that the values of "
            "variables can be inspected?",
            ("Breakpoint", "Syntax highlighting", "Auto-complete", "Pretty printing"),
            0,
            "A breakpoint stops execution at a chosen line. The programmer can then "
            "inspect the variables and step through the code one line at a time to find "
            "where a logic error occurs.",
        ),
        Q(
            "In object-oriented programming, what is encapsulation?",
            (
                "Creating a new class based on an existing one",
                "Keeping attributes private so that they can only be accessed or changed "
                "through the methods of the class",
                "Giving two methods the same name",
                "Creating an object from a class",
            ),
            1,
            "Encapsulation bundles data with the methods that act on it and hides the "
            "attributes behind get and set methods, so an object's data cannot be put "
            "into an invalid state from outside. Basing a class on another is "
            "inheritance, and creating an object is instantiation.",
        ),
    ),
    # --- 2.2.2 Computational methods -------------------------------------------------------
    "2.2.2": (
        Q(
            "Which of these algorithms uses divide and conquer?",
            ("Linear search", "Bubble sort", "Insertion sort", "Merge sort"),
            3,
            "Merge sort repeatedly splits the list in half until each part holds one "
            "item, then merges the parts back together in order. Binary search is another "
            "divide and conquer algorithm.",
        ),
        Q(
            "What is backtracking?",
            (
                "Working methodically towards a solution and returning to an earlier point "
                "to try a different path when one fails",
                "Reversing the order of the items in a list",
                "Running a program backwards to find an error",
                "Storing results so that they can be reused later",
            ),
            0,
            "Backtracking builds a solution one step at a time. When a partial solution "
            "cannot lead to an answer, the algorithm goes back to the last decision and "
            "tries the next option, as in solving a maze or a depth-first search.",
        ),
        Q(
            "When is a heuristic approach appropriate?",
            (
                "When the exact best solution must always be found",
                "When the problem is small enough for every possibility to be checked",
                "When finding the best solution would take too long and a good-enough "
                "solution is acceptable",
                "When the program must use no memory",
            ),
            2,
            "A heuristic is a rule of thumb that gives an acceptable answer in a "
            "reasonable time for problems where finding the optimal answer is "
            "impractical. The A* algorithm uses one to estimate the distance left to the "
            "goal.",
        ),
    ),
    # --- 2.3.1 Algorithms ------------------------------------------------------------------
    "2.3.1": (
        Q(
            "What is the worst-case time complexity of a binary search?",
            ("O(1)", "O(log n)", "O(n)", "O(n^2)"),
            1,
            "Each comparison halves the number of items still to be searched, so the "
            "number of comparisons grows with the logarithm of the size of the list.",
        ),
        Q(
            "What is the worst-case time complexity of a bubble sort?",
            ("O(log n)", "O(n)", "O(n log n)", "O(n^2)"),
            3,
            "In the worst case a bubble sort makes about n passes and compares about n "
            "pairs of items on each pass, giving n * n comparisons.",
        ),
        Q(
            "What is the time complexity of a merge sort?",
            ("O(n log n)", "O(n^2)", "O(log n)", "O(2^n)"),
            0,
            "The list is halved about log n times, and merging the parts back together "
            "at each level takes time proportional to n, which gives O(n log n).",
        ),
        Q(
            "What must be true of a list before a binary search can be used on it?",
            (
                "It must contain no duplicate items",
                "It must have an even number of items",
                "It must be sorted",
                "It must be stored as a linked list",
            ),
            2,
            "Binary search compares the target with the middle item and discards the "
            "half that cannot contain it. That decision is only valid if the items are "
            "in order.",
        ),
        Q(
            "A sorted list holds 1,000 items. What is the maximum number of items a binary "
            "search needs to examine?",
            ("10", "100", "500", "1,000"),
            0,
            "Each comparison halves the search space: 1,000 becomes 500, 250, 125 and so "
            "on. Because 2^10 = 1,024 is the first power of two greater than 1,000, at "
            "most 10 items are examined.",
        ),
        Q(
            "A bubble sort is putting the list [5, 3, 8, 1] into ascending order. What is "
            "the list after the first pass?",
            ("[1, 3, 5, 8]", "[3, 5, 1, 8]", "[3, 5, 8, 1]", "[3, 1, 5, 8]"),
            1,
            "5 and 3 are swapped, giving [3, 5, 8, 1]. 5 and 8 are already in order. 8 "
            "and 1 are swapped, giving [3, 5, 1, 8]. The largest value has now bubbled "
            "to the end of the list.",
        ),
        Q(
            "What does Dijkstra's algorithm find?",
            (
                "The largest value in a binary tree",
                "Whether a list is sorted",
                "The number of nodes in a graph",
                "The shortest path from a start node to the other nodes in a weighted graph",
            ),
            3,
            "Dijkstra's algorithm repeatedly visits the unvisited node with the smallest "
            "known distance from the start and updates the distances to its neighbours, "
            "until the shortest distance to each node is known.",
        ),
        Q(
            "How does the A* algorithm differ from Dijkstra's algorithm?",
            (
                "It only works on unweighted graphs",
                "It visits every node in the graph twice",
                "It uses a heuristic estimate of the distance to the goal to decide which "
                "node to explore next",
                "It always finds a longer path",
            ),
            2,
            "A* adds a heuristic estimate of the remaining distance to the cost so far, "
            "so it explores the nodes that look most promising first and usually reaches "
            "the goal after visiting fewer nodes than Dijkstra's algorithm.",
        ),
        Q(
            "Which traversal of a binary search tree visits the values in ascending order?",
            ("Pre-order", "In-order", "Post-order", "Breadth-first"),
            1,
            "An in-order traversal visits the left subtree, then the node, then the "
            "right subtree. In a binary search tree everything to the left of a node is "
            "smaller and everything to the right is larger, so the values come out "
            "sorted.",
        ),
        Q(
            "Which list puts these time complexities in order from most to least efficient "
            "for large inputs?",
            (
                "O(1), O(log n), O(n), O(n^2)",
                "O(n^2), O(n), O(log n), O(1)",
                "O(log n), O(1), O(n), O(n^2)",
                "O(1), O(n), O(log n), O(n^2)",
            ),
            0,
            "Constant time does not grow at all, logarithmic time grows very slowly, "
            "linear time grows in proportion to the input, and polynomial time grows "
            "much faster as the input gets larger.",
        ),
    ),
}
