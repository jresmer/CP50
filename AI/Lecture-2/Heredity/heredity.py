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
    # joint probability
    joint = 1
    # everyone in set `one_gene` has one copy of the gene
    for person in people:

        prob = 1
        n_genes = 2 if person in two_genes else 1 if person in one_gene else 0

        # person's data
        father = people[person]['father']
        mother = people[person]['mother']
        trait = person in have_trait

        # for someone with parents in the database use parents probabilities
        if father or mother:

            m_prob = PROBS['mutation']
            mother_prob = 0.5 if mother in one_gene else (1 - m_prob) if mother in two_genes else m_prob
            father_prob = 0.5 if father in one_gene else (1 - m_prob) if father in two_genes else m_prob

            # if testing for two genes, then calculate the probability that both father and mother donate a gene each
            if person in two_genes:
                prob *= mother_prob * father_prob
            
            # if testing for one gene, then calculate the probabily that either one of them donates a gene 
            elif person in one_gene:
                prob *= (mother_prob + father_prob - 2 * mother_prob * father_prob)

            # otherwise calculate the probability that neither of the donate a gene
            else:
                prob *= (1 - mother_prob) * (1 - father_prob)

        # if a person does not have parents, then use unconditional probability
        else:
            prob *= PROBS['gene'][n_genes]

        # joint probability of having the trait based on the number of genes
        prob *= PROBS['trait'][n_genes][trait]
        # multiply a person's probabilty to the joint probability
        joint *= prob
        
    return joint


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        # collect person's data
        n_genes = 2 if person in two_genes else 1 if person in one_gene else 0
        trait = person in have_trait

        # update values for their probabilities
        probabilities[person]['gene'][n_genes] += p
        probabilities[person]['trait'][trait] += p
    

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # calculate the sum of all gene probabilities
        E = sum(probabilities[person]['gene'].values())
        # if the sum is not 1, then normalize it
        if E != 1:
            a = 1 / E
            # normalize all probabilities
            for n_genes in probabilities[person]['gene']:
                probabilities[person]['gene'][n_genes] *= a

        # calculate the sum of all trait probabilities
        E = sum(probabilities[person]['trait'].values())
        # if the sum is not 1, then normalize it
        if E != 1:
            a = 1 / E
            # normalize all probabilities
            for n_genes in probabilities[person]['trait']:
                probabilities[person]['trait'][n_genes] *= a


if __name__ == "__main__":
    main()
