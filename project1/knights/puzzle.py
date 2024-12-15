from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Ou A é um Knight ou é um Knave
    Or(And(Not(AKnight), AKnave), And(AKnight, Not(AKnave))), 
    
    # Se ele for um Knight, será Knight e Knave 
    Implication(AKnight, And(AKnight, AKnave)),   
    
    # Se for Knave, será apenas Knave  
    Implication(AKnave, Not(And(AKnight, AKnave)))  
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(And(Not(AKnight), AKnave), And(AKnight, Not(AKnave))),  # A só pode ser um tipo
    Or(And(Not(BKnight), BKnave), And(BKnight, Not(BKnave))),  # B só pode ser um tipo
     
    Implication(AKnight, And(AKnave, BKnave)),  # Se A fala verdade, todos são knaves
    Implication(AKnave, Not(And(AKnave, BKnave)))  # Se A mente, não são ambos knaves
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(And(Not(AKnight), AKnave), And(AKnight, Not(AKnave))),  # A só pode ser um tipo
    Or(And(Not(BKnight), BKnave), And(BKnight, Not(BKnave))),  # B só pode ser um tipo
    
    # Informacoes da fala do A
    # Se A estiver falando verdade, sao do mesmo tipo
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))), 
    # Se A estiver mentindo, são de tipos diferentes
    Implication(AKnave, Or(And(AKnave, BKnight), And(AKnight, BKnave))), 
  
    # Informacoes da fala do B
    # Se B estiver falando verdade, sao de tipos diferentes
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))), 
    # Se B estiver mentindo, são do mesmo tipo
    Implication(BKnave, Or(And(AKnight, BKnight), And(AKnave, BKnave))) 
    
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(And(Not(AKnight), AKnave), And(AKnight, Not(AKnave))),  # A só pode ser um tipo
    Or(And(Not(BKnight), BKnave), And(BKnight, Not(BKnave))),  # B só pode ser um tipo
    Or(And(Not(CKnight), CKnave), And(CKnight, Not(CKnave))),  # C só pode ser um tipo
    
    # Informacoes da fala de A
    # Se A disse que eh um knave, ele nao pode ser um knight, pois knight nao mente, mas ele tambem nao eh um knave,
    # pois um knave falaria que e um knight, pois knave sempre matam, portanto, A so pode ser um knight
    Implication(Or(AKnight, AKnave), AKnight),
    
    # Informacoes da fala de B
    # Se B estiver falando a verdade, A eh um knave e C é um knave, pois disse que A era um knight
    Implication(BKnight, And(AKnave, CKnave)),
    # Se B estiver falando mentira, A eh um knight e C eh um knight, pois disse que A eh um knight
    Implication(BKnave, And(AKnight, CKnight)),
    
    # Informacoes da fala de C
    # Se C estiver falando a verdade, A eh um knight
    Implication(CKnight, AKnight),
    # Se C estiver mentindo, A eh um knave
    Implication(CKnave, AKnave)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
