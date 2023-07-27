import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:

            for word in self.crossword.words:

                # if the word is longer than the number of available cells remove it from domain
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        neighbors = self.crossword.neighbors(x)
        out_ruled = set()

        if y in neighbors:

            cell_x, cell_y = self.crossword.overlaps[x, y]

            for word_y in self.domains[y]:

                # if there is no word in x's domain tha satisfies consistency with word_y, then remove word_y from y's domain
                if not any(word_y[cell_y] == word_x[cell_x] for word_x in self.domains[x]):
                    out_ruled.add(word_y)
                    revised = True

            self.domains[x] -= out_ruled

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            
            arcs = []

            for var1 in self.domains:

                for var2 in self.domains:
                    
                    # if variables are not the same add to 'queue'
                    if var1 != var2:
                        arcs.append((var1, var2))

        while arcs:

            # get a new pair to revise
            x, y = arcs.pop()

            # if a reviision is made
            if self.revise(x, y):

                # if x's domain is empty
                if not self.domains[x]:
                    return False
                
                # add every x neighbor except for y to the 'queue'
                for Z in self.crossword.neighbors(x) - {y}:
                    arcs.append((Z, x))
        
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
             
             # if var not defined in assignment, then return false
             if var not in assignment:
                 return False
             
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_values = set(assignment.values())

        # if a value was assigned to more than one word, then return false
        if len(used_values) != len(assignment):
            return False

        for word1 in assignment:

            # if var's length is different from the assigned wors's length return false
            if len(assignment[word1]) != word1.length:
                return False

            for word2 in self.crossword.neighbors(word1):

                # if neighbor assigned test if overlap constraints are satisfied 
                if word2 in assignment:
                
                    cell1, cell2 = self.crossword.overlaps[word1, word2]

                    # if overlap assignment is inconsistent, then return false
                    if assignment[word1][cell1] != assignment[word2][cell2]:
                        return False

        return True
                    


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values = {}
        variables = self.domains[var]
        neighbors = self.crossword.neighbors(var)

        for value in variables:

            # if a value was already assigned, then ignora variable
            if value in assignment:
                continue

            values[value] = 0

            for neighbor in neighbors:

                for other_value in self.domains[neighbor]:

                    cell1, cell2 = self.crossword.overlap[value][neighbor]

                    # if overlap assignment is inconsistent, add to count
                    if value[cell1] != other_value[cell2]:
                        values[value] += 1

            for variable in self.domains:
                
                # if value is in the domain of a variable, then add to the count
                if value in self.domains[variable]:
                    values[value] += 1

        # return the sorted list
        return sorted(values, key=lambda key : values[key])



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = self.domains.keys() - assignment.keys()

        # return first value of sorted list
        return sorted(unassigned, key=lambda x: (len(self.domains[x]), -len(self.crossword.neighbors(x))))[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if the assignment is complete, then return the assignment
        if self.assignment_complete(assignment):
            return assignment

        # selct unassgigmed variable
        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:

            # assign value 
            assignment[var] = value

            # if the value is consistent, then assign
            if self.consistent(assignment):

                self.ac3([(other_var, var) for other_var in self.crossword.neighbors(var)])
                result = self.backtrack(assignment)

                # if assignment is possible, then return result
                if result:
                    return result

            # otherwise undo assignment
            del assignment[var]

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
