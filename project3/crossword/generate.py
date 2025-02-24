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
        # Para cada variável no domínio
        for var in self.domains:
            # Cria uma cópia do conjunto de palavras para iterar
            words = self.domains[var].copy()
            # Verifica cada palavra no domínio
            for word in words:
                # Se o tamanho da palavra não corresponde ao comprimento da variável
                if len(word) != var.length:
                    # Remove a palavra do domínio
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
        # Obtém a posição de sobreposição entre x e y, se houver
        overlap = self.crossword.overlaps.get((x, y))
        if overlap is not None:
            i, j = overlap  # Índices de sobreposição em x e y
            # Cria uma cópia do domínio de x para iterar
            words_x = self.domains[x].copy()
            for word_x in words_x:
                # Verifica se existe ao menos uma palavra em y que seja compatível
                compatible = False
                for word_y in self.domains[y]:
                    if word_x[i] == word_y[j]:  # Letras na posição de sobreposição coincidem
                        compatible = True
                        break
                # Se nenhuma palavra em y é compatível, remove word_x do domínio de x
                if not compatible:
                    self.domains[x].remove(word_x)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Se arcs não for fornecido, inicializa com todos os arcos possíveis
        if arcs is None:
            arcs = [(x, y) for x in self.crossword.variables for y in self.crossword.variables
                    if x != y and self.crossword.overlaps.get((x, y)) is not None]
        
        # Cria uma fila com os arcos
        queue = list(arcs)
        
        # Enquanto houver arcos na fila
        while queue:
            x, y = queue.pop(0)  # Remove o primeiro arco da fila
            # Se revisar o arco (x, y) altera o domínio de x
            if self.revise(x, y):
                # Se o domínio de x ficou vazio, retorna False (sem solução)
                if not self.domains[x]:
                    return False
                # Adiciona todos os arcos (z, x) de volta à fila, exceto se z for y
                for z in self.crossword.variables:
                    if z != x and z != y and self.crossword.overlaps.get((z, x)) is not None:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Compara o número de variáveis atribuídas com o total de variáveis
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Verifica se todos os valores são distintos
        values = list(assignment.values())
        if len(values) != len(set(values)):
            return False

        # Verifica se cada palavra tem o tamanho correto e não há conflitos
        for var, word in assignment.items():
            # Verifica o comprimento da palavra
            if len(word) != var.length:
                return False
            # Verifica conflitos com outras variáveis no assignment
            for other_var, other_word in assignment.items():
                if var != other_var:
                    overlap = self.crossword.overlaps.get((var, other_var))
                    if overlap:
                        i, j = overlap
                        if word[i] != other_word[j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Lista para armazenar valores e contagem de eliminações
        value_counts = []
        
        # Para cada valor no domínio de var
        for value in self.domains[var]:
            count = 0
            # Verifica vizinhos não atribuídos
            for neighbor in self.crossword.variables:
                if neighbor not in assignment and neighbor != var:
                    overlap = self.crossword.overlaps.get((var, neighbor))
                    if overlap:
                        i, j = overlap
                        # Conta quantos valores do vizinho seriam eliminados
                        for neighbor_value in self.domains[neighbor]:
                            if value[i] != neighbor_value[j]:
                                count += 1
            value_counts.append((value, count))
        
        # Ordena pelo número de eliminações (menor primeiro)
        value_counts.sort(key=lambda x: x[1])
        # Retorna apenas os valores, sem as contagens
        return [value for value, _ in value_counts]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [var for var in self.crossword.variables if var not in assignment]
        if not unassigned:
            return None
        
        # Ordena por número de valores restantes (MRV)
        unassigned.sort(key=lambda var: len(self.domains[var]))
        
        # Pega o menor número de valores restantes
        min_values = len(self.domains[unassigned[0]])
        candidates = [var for var in unassigned if len(self.domains[var]) == min_values]
        
        # Em caso de empate, escolhe pelo maior grau (número de vizinhos)
        if len(candidates) > 1:
            candidates.sort(key=lambda var: sum(1 for v in self.crossword.variables if v != var and self.crossword.overlaps.get((var, v)) is not None),
                            reverse=True)
        
        return candidates[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Se assignment está completo, verifica consistência e retorna
        if self.assignment_complete(assignment):
            return assignment if self.consistent(assignment) else None
        
        # Seleciona uma variável não atribuída
        var = self.select_unassigned_variable(assignment)
        if var is None:
            return None
        
        # Para cada valor no domínio de var (ordenado por heurística)
        for value in self.order_domain_values(var, assignment):
            # Cria uma cópia do assignment atual
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            # Verifica se a nova atribuição é consistente
            if self.consistent(new_assignment):
                # Faz uma cópia dos domínios atuais
                old_domains = {v: self.domains[v].copy() for v in self.domains}
                # Tenta resolver recursivamente
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                # Restaura os domínios se falhar
                self.domains = old_domains
        
        # Se nenhum valor funcionar, retorna None
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