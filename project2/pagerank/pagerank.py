import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Novo dicionário
    probabilities = {key: 0.0 for key in corpus}
    numPages = len(probabilities)
    
    # Verificando se page tem links de saída
    if len(corpus[page]) == 0:
        for key in corpus:
            # Mesma probabilidade para todas páginas
            probabilities[key] = 1.0/numPages
    # Caso o page tenha um ou mais links
    else:
        # Probabilidade = Damping Factor
        for link in corpus[page]:
            probabilities[link] = damping_factor / len(corpus[page])
        
        # Probabilidade =  1 - Damping Factor
        for link in probabilities:
            probabilities[link] += (1 - damping_factor) / len(probabilities)
    
    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Novo dicionário
    sampleRank = {key: 0.0 for key in corpus}
    # Primeira página escolhida aleatoriamente
    chosenPage = random.choice(list(sampleRank.keys()))
    sampleRank[chosenPage] += 1.0
    
    for _ in range(n-1):
        # Gera as probabilidades de escolhe cada página, dada a página atual
        probabilities = transition_model(corpus, chosenPage, damping_factor)
        
        # Escolhe a próxima página atual, baseada nas probabilidades do modelo de transição da amostra anterior
        chosenPage = random.choices(list(probabilities.keys()), weights=probabilities.values())[0]
        
        # Aumenta a contagem de vezes em que a pagina foi escolhida
        sampleRank[chosenPage] += 1.0
    
    # Calcula a proporção de amostras que correspondem à cada página
    for page in sampleRank:
        sampleRank[page] = sampleRank[page] / n
    
    return sampleRank
  
      
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Novo dicionário
    iterateRank = {key: 0.0 for key in corpus}
    # Variável de controle para continuar o cálculo iterativo
    keepUpdate = True
    
    # Classificação inicial = 1 / N
    for page in iterateRank:
        iterateRank[page] = 1.0 / len(iterateRank)
    
    # Dicionário para manter valores da iteração anterior para verificar a necessidade de continuar os cálculos
    oldValues = {key: 0.0 for key in iterateRank}
    
    # Calcular classificação de todas as páginas page que fazem link para página pr
    while (keepUpdate):
        for pr in iterateRank:
            sum = 0.0
            # Contabiliza-se as páginas que tem link para página pr
            for page in corpus:
                # Caso a page não tenha links, considera-se links para todas as páginas, inclusive ela mesma
                if not corpus[page]:
                    numLinks = len(corpus)  
                    # Somatório
                    sum += iterateRank[page] / numLinks
                # Caso a página page tenha link para a página pr, contabiliza-se todos os links que page possui      
                if pr in corpus[page]:
                    numLinks = len(corpus[page])
                    # Somatório
                    sum += iterateRank[page] / numLinks
              
            # Atualiza o pageRank
            oldValues[pr] = iterateRank[pr]
            iterateRank[pr] = ((1 - damping_factor) / len(corpus)) + damping_factor * sum
        # Verifica se deve continuar efetuando cálculos
        keepUpdate = False
        for page in oldValues:
            # Caso algum valor seja alterado em um um valor maior que 0.001, deve se calcular mais uma iteração
            if (abs(oldValues[page] - iterateRank[page]) > 0.001):
                keepUpdate = True
                
    return iterateRank
                
                         
if __name__ == "__main__":
    main()
