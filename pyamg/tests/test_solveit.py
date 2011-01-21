from pyamg.testing import *

from numpy import matrix, array, diag, arange, ones, zeros_like, random
from scipy import rand
from scipy.linalg import norm
from pyamg.gallery import poisson, load_example 
from pyamg import solveit

class TestSolveit(TestCase):
    def setUp(self):
        self.cases = []

        # Poisson problems in 1D and 2D
        N = 30
        self.cases.append( (poisson( (N,), format='csr'), rand(N,)) )     # 0
        self.cases.append( (poisson( (N,N), format='csr'), rand(N*N,)) )  # 1
        # Boxed examples
        A = load_example('recirc_flow')['A'].tocsr()                      # 2
        self.cases.append( (A, rand(A.shape[0],) ))
        A = load_example('bar')['A'].tobsr(blocksize=(3,3))               # 3
        self.cases.append( (A, rand(A.shape[0],) ))
                        

    def test_solveit(self):
        for A,b in self.cases:
            x = solveit(A,b,verb=False)
            assert( norm(b - A*x)/norm(b - A*rand(b.shape[0],)) < 1e-4 )

        ##
        # Special tests
        #(1) Make sure BSR format is preserved, and B is multiple vecs
        A,b = self.cases[-1]
        (x,ml) = solveit(A,b,return_solver=True,verb=False)
        assert(ml.levels[0].B.shape[1] == 3)
        assert(ml.levels[0].A.format == 'bsr')
        
        #(2) Run with solver and make sure that solution is still good
        x = solveit(A,b,solver=ml,verb=False)
        assert( norm(b - A*x)/norm(b - A*rand(b.shape[0],)) < 1e-4 )

        #(3) Convert to CSR, make sure B is a single vector
        (x,ml) = solveit(A.tocsr(),b,return_solver=True,verb=False)
        assert(ml.levels[0].B.shape[1] == 1)
        assert(ml.levels[0].A.format == 'csr')
         
        #(4) Run with x0, maxiter and tol
        x = solveit(A,b,solver=ml,x0=zeros_like(b), tol=1e-8, maxiter=300,verb=False)
        assert( norm(b - A*x)/norm(b - A*rand(b.shape[0],)) < 1e-7 )
 
        #(5) Run nonsymmetric example, make sure BH isn't None
        A,b = self.cases[2]
        (x,ml) = solveit(A,b,return_solver=True,verb=False)
        assert(ml.levels[0].BH != None)

