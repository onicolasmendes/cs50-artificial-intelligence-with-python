import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Probabilidade final com elemento neutro da multiplicação
    final_probability = 1.00
    
    # Verificar todo o dicionário
    for person in people:
        # Informações individuais sobre cada pessoa
        
        # Extraindo quantidade de genes, existencia da caracteristica e probabilidade de ter ou não a caracteristica
        gene = 1 if person in one_gene else 2 if person in two_genes else 0
        trait = True if person in have_trait else False
        trait_prob = PROBS["trait"][gene][trait]
        # Pais
        mother = people[person]["mother"]
        father = people[person]["father"]
        
        # Caso não tenha os pais listados, usa-se os valores padrões
        if not mother and not father:
            probability = PROBS["gene"][gene]
        # Caso os pais estejam listados
        else:
            # Quantidadede dos genes para o pai e a mae
            gene_mother = 2 if mother in two_genes else 1 if mother in one_gene else 0
            gene_father = 2 if father in two_genes else 1 if father in one_gene else 0
            
            # Probabilidade do pai e da mae passarem o gene (ou genes) para o filho - 0.01 caso não tenha nennum gene, 0,5 acaso haja um gene, 99 casa haja dois genes
            prob_mother = 0.5 if gene_mother == 1 else 0.01 if gene_mother == 0 else 0.99
            prob_father = 0.5 if gene_father == 1 else 0.01 if gene_father == 0 else 0.99
            
            # Cálculo das probabilidades, avaliando as probabilidades do pai e da mae
            # Caso em que se deseja saber se a probilidade de não herdar o gene
            if gene == 0:
                probability = (1 - prob_mother) * (1 - prob_father)
            # Caso em que se deseja saber se a probilidade de herdar um gene
            elif gene == 1:
                probability = ((1 - prob_mother) * prob_father) + ((1 - prob_father) * prob_mother)
            # Caso em que se deseja saber se a probilidade de herdar dois genes
            else:
                probability = prob_mother * prob_father
            
        # Produto com as probabilidades anteriormente calculadas
        final_probability *= probability * trait_prob
        
    return final_probability
 
            
def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    
    # Percorre o dicionário
    for person in probabilities:
        # Obtenção dos índices do dicionário para atualização
        gene = 2 if person in two_genes else 1 if person in one_gene else 0
        trait = True if person in have_trait else False
        
        # Atualização dos índices propriamente ditos
        probabilities[person]["gene"][gene] += p
        probabilities[person]["trait"][trait] += p
   
    
def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Percorre todo o dicionário
    for person in probabilities:
        # Percorre as distribuições que serão normalizadas
        distribuicoes = probabilities[person]
        for distribuicao in distribuicoes:
            # Soma os valores da distribuicao para posteriomente dividir no processo de normalização
            total = sum(probabilities[person][distribuicao].values())
            # Normaliza todos os valores da distribuição dividindo pela soma total
            for value in probabilities[person][distribuicao]:
                probabilities[person][distribuicao][value] /= total


if __name__ == "__main__":
    main()
