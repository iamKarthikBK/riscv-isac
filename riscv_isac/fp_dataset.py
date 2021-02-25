from riscv_isac.log import logger
import itertools
import random
import sys

fzero       = ['0x00000000', '0x80000000']
fminsubnorm = ['0x00000001', '0x80000001']
fsubnorm    = ['0x00000002', '0x80000002', '0x007FFFFE', '0x807FFFFE', '0x00555555', '0x80555555']
fmaxsubnorm = ['0x007FFFFF', '0x807FFFFF']
fminnorm    = ['0x00800000', '0x80800000']
fnorm       = ['0x00800001', '0x80800001', '0x00855555', '0x80855555', '0x008AAAAA', '0x808AAAAA', '0x55000000', '0xD5000000', '0x2A000000', '0xAA000000']
fmaxnorm    = ['0x7F7FFFFF', '0xFF7FFFFF']
finfinity   = ['0x7F800000', '0xFF800000']
fdefaultnan = ['0x7FC00000', '0xFFC00000']
fqnan       = ['0x7FC00001', '0xFFC00001', '0x7FC55555', '0xFFC55555']
fsnan       = ['0x7F800001', '0xFF800001', '0x7FAAAAAA', '0xFFAAAAAA']
fone        = ['0x3F800000', '0xBF800000']

dzero       = ['0x0000000000000000', '0x8000000000000000']
dminsubnorm = ['0x0000000000000001', '0x8000000000000001']
dsubnorm    = ['0x0000000000000002', '0x8000000000000002']
dmaxsubnorm = ['0x000FFFFFFFFFFFFF', '0x800FFFFFFFFFFFFF']
dminnorm    = ['0x0010000000000000', '0x8010000000000000']
dnorm       = ['0x0010000000000002', '0x8010000000000002']
dmaxnorm    = ['0x7FEFFFFFFFFFFFFF', '0xFFEFFFFFFFFFFFFF']
dinfinity   = ['0x7FF0000000000000', '0xFFF0000000000000']
ddefaultnan = ['0x7FF8000000000000', '0xFFF8000000000000']
dqnan       = ['0x7FF8000000000001', '0xFFF8000000000001']
dsnan       = ['0x7FF0000000000001', '0xFFF0000000000001']
done        = ['0x3FF0000000000000', '0xBF80000000000000']

rounding_modes = ['0','1','2','3','4']

def num_explain(num):
	num_dict = {
		tuple(fzero) 		: 'fzero',
		tuple(fminsubnorm) 	: 'fminsubnorm',
		tuple(fsubnorm) 	: 'fsubnorm',
		tuple(fmaxsubnorm) 	: 'fmaxsubnorm',
		tuple(fminnorm) 	: 'fminnorm',
		tuple(fnorm) 		: 'fnorm',
		tuple(fmaxnorm) 	: 'fmaxnorm',
		tuple(finfinity) 	: 'finfinity',
		tuple(fdefaultnan) 	: 'fdefaultnan',
		tuple(fqnan) 		: 'fqnan',
		tuple(fsnan) 		: 'fsnan',
		tuple(fone) 		: 'fone',
		tuple(dzero) 		: 'dzero',
		tuple(dminsubnorm) 	: 'dminsubnorm',
		tuple(dsubnorm) 	: 'dsubnorm',
		tuple(dmaxsubnorm) 	: 'dmaxsubnorm',
		tuple(dminnorm) 	: 'dminnorm',
		tuple(dnorm) 		: 'dnorm',
		tuple(dmaxnorm) 	: 'dmaxnorm',
		tuple(dinfinity) 	: 'dinfinity',
		tuple(ddefaultnan) 	: 'ddefaultnan',
		tuple(dqnan) 		: 'dqnan',
		tuple(dsnan) 		: 'dsnan',
		tuple(done) 		: 'done'
	}
	num_list = list(num_dict.items())
	for i in range(len(num_list)):
		if(num in num_list[i][0]):
			return(num_list[i][1])

def extract_fields(flen, hexstr, postfix):
    if flen == 32:
        e_sz = 8
        m_sz = 23
    else:
        e_sz = 11
        m_sz = 52
    bin_val = bin(int('1'+hexstr[2:],16))[3:]
    sgn = bin_val[0]
    exp = bin_val[1:e_sz+1]
    man = bin_val[e_sz+1:]

    string = 'fs'+postfix+' == '+str(sgn) +\
            ' and fe'+postfix+' == '+str(hex(int(exp,2))) +\
            ' and fm'+postfix+' == '+str(hex(int(man,2)))

    return string

def ibm_b1(flen, ops):
    '''
    Test all combinations of floating-point basic types, positive and negative, for
    each of the inputs. The basic types are Zero, One, MinSubNorm, SubNorm,
    MaxSubNorm, MinNorm, Norm, MaxNorm, Infinity, DefaultNaN, QNaN, and
    SNaN.
    '''
    if flen == 32:
        basic_types = fzero + fminsubnorm + [fsubnorm[0], fsubnorm[3]] +\
            fmaxsubnorm + fminnorm + [fnorm[0], fnorm[3]] + fmaxnorm + \
            finfinity + fdefaultnan + [fqnan[0], fqnan[3]] + \
            [fsnan[0], fsnan[3]] + fone
    elif flen == 64:
    	basic_types = dzero + dminsubnorm + [dsubnorm[0], dsubnorm[1]] +\
            dmaxsubnorm + dminnorm + [dnorm[0], fnorm[1]] + dmaxnorm + \
            dinfinity + ddefaultnan + [dqnan[0], dqnan[1]] + \
            [dsnan[0], dsnan[1]] + done
    else:
        logger.error('Invalid flen value!')
        sys.exit(1)
    
    # the following creates a cross product for ops number of variables
    b1_comb = list(itertools.product(*ops*[basic_types]))
    coverpoints = []
    for c in b1_comb:
        cvpt = ""
        for x in range(1, ops+1):
#            cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
            cvpt += (extract_fields(flen,c[x-1],str(x)))
            cvpt += " and "
        cvpt += "rm == 0 #"
        for y in range(1, ops+1):
            cvpt += 'rs'+str(y)+'_val=='
            cvpt += num_explain(c[y-1]) + '(' + str(c[y-1]) + ')'
            if(y != ops):
            	cvpt += " and "
        coverpoints.append(cvpt)
    
    mess='Generated '+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B1!'
    logger.info(mess)
    
    return coverpoints
    
def ibm_b2(flen, ops):
	'''
	This model tests final results that are very close, measured in Hamming distance,
	to the specified boundary values. Each boundary value is taken as a base value, 
	and the model enumerates over small deviations from the base, by flipping one bit 
	of the significand.
	'''
	if flen == 32:
		flip_types = fzero + fone + fminsubnorm + fmaxsubnorm + fminnorm + fmaxnorm
		b = '0x00000001'
	elif flen == 64:
		flip_types = dzero + done + dminsubnorm + dmaxsubnorm + dminnorm + dmaxnorm
		b = '0x0000000000000001'
		
	result = []
	for i in range(len(flip_types)):
		result.append('0x' + hex(int('1'+flip_types[i][2:], 16) ^ int(b[2:], 16))[3:])
		
	# the following creates a cross product for ops number of variables
	b2_comm = list(itertools.product(*ops*[flip_types]))
	b2_comb = list(itertools.product(*ops*[result]))
	coverpoints = []
	for c,d in zip(b2_comb,b2_comm):
		cvpt = ""
		for x in range(1, ops+1):
#            cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		cvpt += "rm == 0 #"
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += 'Flipped Last Bit of '+ num_explain(d[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		coverpoints.append(cvpt)
		
	mess='Generated '+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B2!'
	logger.info(mess)

	return coverpoints

