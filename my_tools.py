import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import names

all_names = set(names.words())
lemmatizer = WordNetLemmatizer()

def letters_only(astr):
    return astr.isalpha()

def clean_text(docs):
    cleaned_docs = []
       
    for d in docs:
        cleaned_docs.append(
            ' '.join([lemmatizer.lemmatize(word.lower())
            for word in d.split()
            if letters_only(word) and word not in all_names]))
    return cleaned_docs

def get_prior(label_index):
    """
    Compute prior based on training samples
    Args:
        label_index (grouped sample indices by class)
    Returns:
        dictionary, with class label as key, corresponding
        prior as the value
    """

    prior = {label: len(index) for label, index in label_index.items()}
    total_count = sum(prior.values())
    for label in prior:
        prior[label] /= float(total_count)
    return prior

def get_posterior(term_document_matrix, prior, likelihood):
    """ Compute posterior of testing samples, based on prior and
    likelihood
    Args:
        term_document_matrix (sparce matrix)
        prior (dictionary, with class label as key, corresponding prior as the value)
        likelihood (dictionary, with class label as key, corresponding conditional
        probability vector as value)
    Returns:
        dictionary, with class label as key, corresponding
        posterior as value
    """

    num_docs = term_document_matrix.shape[0]
    posteriors = []
    for i in range(num_docs):
        # posterior is proportional to prior * likelihood
        # = exp(log(prior * likelihood))
        # = exp(log(prior) + log(likelihood))

        posterior = { key:np.log(prior_label) for key, prior_label in prior.items()}

        for label, likelihood_label in likelihood.items():
            term_document_vector = term_document_matrix.getrow(i)
            counts = term_document_vector.data
            indices = term_document_vector.indices
            for count, index in zip(counts, indices):
                posterior[label] += np.log(likelihood_label[index] * count)
                # exp(-1000):exp(-999) will cause zero division error,
                #however it equates to exp(0):exp(1)

        min_log_posterior = min(posterior.values())
        for label in posterior:
            try:
                posterior[label] = np.exp(posterior[label] - min_log_posterior)
            except:
                # if one's log value is excessively large, assign it to infinity
                posterior[label] = float('inf')

        # normalize so that all sums up to 1
        sum_posterior = sum(posterior.values())
        for label in posterior:
            if posterior[label] == float('inf'):
                posterior[label] = 1.0
            else:
                posterior[label] /= sum_posterior

        posteriors.append(posterior.copy())

    return posteriors

def get_likelihood(term_document_matrix, label_index, smoothing=0):
    """ Compute likelihood based on training samples
    Args:
        term_document_matrix (sparce matrix)
        label_index (grouped sample indices by class)
        smoothing (integer, additive Laplace smoothing)
    Returns:
        dictionary, with class as key, corresponding conditional
        probability P(feature|class) vector as value.
    """
    likelihood = {}

    for label, index in label_index.items():
        likelihood[label] = term_document_matrix[index, :].sum(axis=0) + smoothing
        likelihood[label] = np.asarray(likelihood[label])[0]
        total_count = likelihood[label].sum()
        likelihood[label] = likelihood[label] / float(total_count)
    return likelihood



def get_label_index(labels):
    from collections import defaultdict
    label_index = defaultdict(list)
    for index, label in enumerate(labels):
        label_index[label].append(index)
    return label_index
