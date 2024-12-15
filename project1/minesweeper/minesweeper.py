import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        
        # A quantidade de bombas eh igual a quantidade de celulas
        if self.count == len(self.cells):
            mines = copy.deepcopy(self.cells)
            
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        
        safe = set()
        
        # Nao ha bombas em nenhuma das celulas
        if self.count == 0:
            safe = copy.deepcopy(self.cells)
        
        return safe
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Se a celula bomba estiver nas celulas da sentenca, ela eh removida
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Se a celula segura estiver nas celulas da sentenca, ela eh removida
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Adiciona a celula a celulas exploradas - step 1
        self.moves_made.add(cell)
        
        # Adiciona a celula a celulas seguras - step 2
        self.mark_safe(cell)
        
        # Mapeia os vizinhos - step 3
        # Obtem todas as celulas vizinhas
        neighbors_cells, count = self.get_neighbors(cell, count)
        # Remove as que são sabidamente seguras e bomba
        neighbors_cells -= self.mines
        neighbors_cells -= self.safes
        
        if neighbors_cells:
            new_sentence = Sentence(neighbors_cells, count)
            self.knowledge.append(new_sentence)
        # Atualizando as senbencas da base de conhecimento - step 4
        update = True
        while update:
            update = False
        
            # Verifica todas as setencas    
            for sentence in self.knowledge:
                # Obtem todas as celulas seguras e bombas conhecidas
                safes = sentence.known_safes()
                mines = sentence.known_mines()             
            
                # Atualiza caso haja uma celula bomba que nao esteja mapeada na base de conhecimento
                if len(mines) != 0:
                    for mine in mines:
                        if mine not in self.mines:
                            self.mark_mine(mine)
                            update = True
                            
                # Atualiza caso haja uma celula segura que nao esteja mapeada na base de conhecimento
                if len(safes) != 0:
                    for safe in safes:
                        if safe not in self.safes:
                            self.mark_safe(safe)
                            update = True
                            
        # Removendo sentencas com celulas vazias
        self.knowledge = [sentence for sentence in self.knowledge if sentence.cells]
        
        # Cria novas sentencas, caso possam ser inferidas - step 5
        for sentence in self.knowledge:
            for sentence1 in self.knowledge:
                if sentence == sentence1:
                    continue
                # Verifica se as celulas de uma sentenca eh um subconjunto da outra
                if sentence.cells.issubset(sentence1.cells):
                    # Subtrai os conjuntos de celulas e os contadores
                    sentence_cells = sentence1.cells - sentence.cells
                    senence_count = sentence1.count - sentence.count
                    new_sentence = Sentence(sentence_cells, senence_count)
                    # Verifica se a setenca ja existe na base de conhecimento
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                        update = True
                           
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Verifica se nao foi feito um movimento com uma celula sabidamente segura
        if len(self.safes) != 0:
            for safe in self.safes:
                if safe not in self.moves_made:
                    return copy.deepcopy(safe)
                
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Caso em que o jogo iniciou, moves made vazio
        if len(self.moves_made) == 0:
            move = (random.randint(0, self.height - 1,), random.randint(0, self.width - 1))
            return move
        
        # Caso em que move made não esta vazio
        validCells = set()
        # Obtem todas as celulas validas do jogo
        for i in range(self.height):
            for j in range(self.width):
                validCells.add((i, j))
        
        for i in range(self.height):
            for j in range(self.width):
                # Se a celula nao eh uma bomba e tambem nao foi explorada no jogo, ela eh adicionada
                if ((i, j) not in self.moves_made) and ((i, j) not in self.mines):
                    return (i, j)
        
        # Escolhe aleatoriamente uma celula para representar a jogada
        if len(validCells) > 0:
            return random.choice(list(validCells))
              
    def get_neighbors(self, cell, count):
        neighbors_cells = set()
        i, j = cell
    
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                # Verifica se os indices estao dentro dos limites da matriz
                if 0 <= x < self.height and 0 <= y < self.width:
                    if (x, y) != cell and (x, y) not in self.safes:
                        # Caso nao seja uma celula bomba, eh adicionada as celulas vizinhas
                        if (x, y) not in self.mines:
                            neighbors_cells.add((x, y))
                        # Caso seja uma celula bomba, a celula nao eh adicionada e o contador eh decrementado em funcao disso
                        else:
                            count -= 1

        return neighbors_cells, count
    
