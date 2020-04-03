import torch


def log_domain_matmul(log_A, log_B, use_max=False):
    """
    log_A : m x n
    log_B : n x p

    output : m x p matrix

    Normally, a matrix multiplication
    computes out_{i,j} = sum_k A_{i,k} x B_{k,j}

    A log domain matrix multiplication
    computes out_{i,j} = logsumexp_k log_A_{i,k} + log_B_{k,j}

    This is needed for numerical stability
    when A and B are probability matrices.
    """
    try:
        import genbmm

        out = genbmm.logbmm(
            log_A.unsqueeze(0).contiguous(), log_B.unsqueeze(1).contiguous()
        )[0]
    except ModuleNotFoundError:
        m = log_A.shape[0]
        n = log_A.shape[1]
        p = log_B.shape[1]

        log_A_expanded = torch.stack([log_A] * p, dim=2)
        log_B_expanded = torch.stack([log_B] * m, dim=0)

        elementwise_sum = log_A_expanded + log_B_expanded
        out = torch.logsumexp(elementwise_sum, dim=1)
    return out


def maxmul(log_A, log_B):
    m = log_A.shape[0]
    n = log_A.shape[1]
    p = log_B.shape[1]

    log_A_expanded = torch.stack([log_A] * p, dim=2)
    log_B_expanded = torch.stack([log_B] * m, dim=0)

    elementwise_sum = log_A_expanded + log_B_expanded
    out1, out2 = torch.max(elementwise_sum, dim=1)

    return out1, out2
