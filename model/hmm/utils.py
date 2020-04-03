import torch


def log_domain_matmul(log_A, log_B):
    """
    log_A : p x m x n
    log_B : n x p

    output : m x p matrix

    Normally, a matrix multiplication
    computes out_{i,j} = sum_k A_{i,k} x B_{k,j}

    A log domain matrix multiplication
    computes out_{i,j} = logsumexp_k log_A_{i,k} + log_B_{k,j}

    This is needed for numerical stability
    when A and B are probability matrices.
    """
    m = log_A.shape[1]
    n = log_A.shape[2]
    p = log_B.shape[1]

    log_A_expanded = log_A.transpose(0, 1).transpose(1, 2)
    log_B_expanded = torch.stack([log_B] * m, dim=0)

    elementwise_sum = log_A_expanded + log_B_expanded
    out = torch.logsumexp(elementwise_sum, dim=1)
    return out


def maxmul(log_A, log_B):
    m = log_A.shape[1]
    n = log_A.shape[2]
    p = log_B.shape[1]

    log_A_expanded = log_A.transpose(0, 1).transpose(1, 2)
    log_B_expanded = torch.stack([log_B] * m, dim=0)

    elementwise_sum = log_A_expanded + log_B_expanded
    out1, out2 = torch.max(elementwise_sum, dim=1)

    return out1, out2
