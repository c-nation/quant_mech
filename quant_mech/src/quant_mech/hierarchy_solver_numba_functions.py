'''
Created on 19 Aug 2016

@author: rstones
'''
import numpy as np
import numba

@numba.jit(nopython=True, cache=True)
def generate_hierarchy_and_tier_couplings(num_dms, num_indices, truncation_level, dm_per_tier):#, scaling_factors):
    
    hierarchy = np.zeros((num_dms, num_indices))
    
    tier_start_indices = np.zeros(truncation_level+1, dtype=np.int32)
    for i in range(dm_per_tier.size):
        tier_start_indices[i] = np.sum(dm_per_tier[:i])
    
#     higher_coupling_matrices = np.zeros((num_indices, num_dms, num_dms), dtype=np.complex64)
#     lower_coupling_matrices = np.zeros((num_indices, num_dms, num_dms), dtype=np.complex64)
    
    '''
    Semi-implementation of sparse matrices here
    Put elements and row/column indices in arrays
    Create sparse coo_matrix back in python land
    '''
    num_non_zero_elements_per_idx = num_dms-dm_per_tier[-2] # [-2] because dm_per_tier has dm for one index higher than required for ease
    higher_coupling_elements = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.complex128)
    higher_coupling_row_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    higher_coupling_column_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    lower_coupling_elements = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.complex128)
    lower_coupling_row_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    lower_coupling_column_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    current_non_zero_element_idx = 0
    
    next_level = 1
    
    while next_level < truncation_level:
        hierarchy_next_level = hierarchy[tier_start_indices[next_level]:tier_start_indices[next_level+1]]
        previous_level = hierarchy[tier_start_indices[next_level-1]:tier_start_indices[next_level]]
        for i in range(previous_level.shape[0]):
            vec = previous_level[i]
            for n in range(vec.size):
                vec[n] += 1
                for j in range(hierarchy_next_level.shape[0]):
                    r = hierarchy_next_level[j]
                    in_array = True
                    zero_vec = True
                    for k in range(r.size):
                        if r[k] != 0:
                            zero_vec = False
                        if r[k] != vec[k]:
                            in_array = False
                    if zero_vec:
                        hierarchy_next_level[j] = vec
                        current_tier_vec_idx = j
                        break
                    elif in_array:
                        current_tier_vec_idx = j
                        break
                #lower_coupling_matrices[n][tier_start_indices[next_level]+current_tier_vec_idx, tier_start_indices[next_level-1]+i] = np.sqrt(vec[n] / scaling_factors[n])
                lower_coupling_elements[n, current_non_zero_element_idx] = np.sqrt(vec[n]) #np.sqrt(vec[n] / scaling_factors[n])
                lower_coupling_row_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level]+current_tier_vec_idx
                lower_coupling_column_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level-1]+i
                vec[n] -= 1
                #higher_coupling_matrices[n][tier_start_indices[next_level-1]+i, tier_start_indices[next_level]+current_tier_vec_idx] = np.sqrt((vec[n]+1)*scaling_factors[n])
                higher_coupling_elements[n, current_non_zero_element_idx] = np.sqrt((vec[n]+1)) # np.sqrt((vec[n]+1)*scaling_factors[n])
                higher_coupling_row_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level-1]+i
                higher_coupling_column_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level]+current_tier_vec_idx
            current_non_zero_element_idx += 1
        next_level += 1
    
    #return hierarchy, higher_coupling_matrices, lower_coupling_matrices
    return hierarchy, higher_coupling_elements, higher_coupling_row_indices, higher_coupling_column_indices, \
                            lower_coupling_elements, lower_coupling_row_indices, lower_coupling_column_indices
                            
@numba.jit(nopython=True, cache=True)
def generate_hierarchy_and_tier_couplings_nonrenorm(num_dms, num_indices, truncation_level, dm_per_tier):#, scaling_factors):
    
    hierarchy = np.zeros((num_dms, num_indices))
    
    tier_start_indices = np.zeros(truncation_level+1, dtype=np.int32)
    for i in range(dm_per_tier.size):
        tier_start_indices[i] = np.sum(dm_per_tier[:i])
    
#     higher_coupling_matrices = np.zeros((num_indices, num_dms, num_dms), dtype=np.complex64)
#     lower_coupling_matrices = np.zeros((num_indices, num_dms, num_dms), dtype=np.complex64)
    
    '''
    Semi-implementation of sparse matrices here
    Put elements and row/column indices in arrays
    Create sparse coo_matrix back in python land
    '''
    num_non_zero_elements_per_idx = num_dms-dm_per_tier[-2] # [-2] because dm_per_tier has dm for one index higher than required for ease
    higher_coupling_elements = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.complex128)
    higher_coupling_row_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    higher_coupling_column_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    lower_coupling_elements = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.complex128)
    lower_coupling_row_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    lower_coupling_column_indices = np.zeros((num_indices, num_non_zero_elements_per_idx), dtype=np.int32)
    current_non_zero_element_idx = 0
    
    next_level = 1
    
    while next_level < truncation_level:
        hierarchy_next_level = hierarchy[tier_start_indices[next_level]:tier_start_indices[next_level+1]]
        previous_level = hierarchy[tier_start_indices[next_level-1]:tier_start_indices[next_level]]
        for i in range(previous_level.shape[0]):
            vec = previous_level[i]
            for n in range(vec.size):
                vec[n] += 1
                for j in range(hierarchy_next_level.shape[0]):
                    r = hierarchy_next_level[j]
                    in_array = True
                    zero_vec = True
                    for k in range(r.size):
                        if r[k] != 0:
                            zero_vec = False
                        if r[k] != vec[k]:
                            in_array = False
                    if zero_vec:
                        hierarchy_next_level[j] = vec
                        current_tier_vec_idx = j
                        break
                    elif in_array:
                        current_tier_vec_idx = j
                        break
                #lower_coupling_matrices[n][tier_start_indices[next_level]+current_tier_vec_idx, tier_start_indices[next_level-1]+i] = np.sqrt(vec[n] / scaling_factors[n])
                lower_coupling_elements[n, current_non_zero_element_idx] = vec[n]
                lower_coupling_row_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level]+current_tier_vec_idx
                lower_coupling_column_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level-1]+i
                vec[n] -= 1
                #higher_coupling_matrices[n][tier_start_indices[next_level-1]+i, tier_start_indices[next_level]+current_tier_vec_idx] = np.sqrt((vec[n]+1)*scaling_factors[n])
                higher_coupling_elements[n, current_non_zero_element_idx] = 1.
                higher_coupling_row_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level-1]+i
                higher_coupling_column_indices[n, current_non_zero_element_idx] = tier_start_indices[next_level]+current_tier_vec_idx
            current_non_zero_element_idx += 1
        next_level += 1
    
    #return hierarchy, higher_coupling_matrices, lower_coupling_matrices
    return hierarchy, higher_coupling_elements, higher_coupling_row_indices, higher_coupling_column_indices, \
                            lower_coupling_elements, lower_coupling_row_indices, lower_coupling_column_indices