# Program that implements a multi-dimensional Kalman Filter

import numpy as np

class matrix:
    
    # Implements basic operations of a matrix class
    
    def __init__(self, value):
        self.value = value
        self.dimx = len(value)
        self.dimy = len(value[0])
        if value == [[]]:
            self.dimx = 0
    
    def zero(self, dimx, dimy):
        # check if valid dimensions
        if dimx < 1 or dimy < 1:
            raise ValueError, "Invalid size of matrix"
        else:
            self.dimx = dimx
            self.dimy = dimy
            self.value = [[0 for row in range(dimy)] for col in range(dimx)]
    
    def identity(self, dim):
        # check if valid dimension
        if dim < 1:
            raise ValueError, "Invalid size of matrix"
        else:
            self.dimx = dim
            self.dimy = dim
            self.value = [[0 for row in range(dim)] for col in range(dim)]
            for i in range(dim):
                self.value[i][i] = 1
    
    def show(self):
        for i in range(self.dimx):
            print self.value[i]
        print ' '
    
    def __add__(self, other):
        # check if correct dimensions
        if self.dimx != other.dimx or self.dimy != other.dimy:
            raise ValueError, "Matrices must be of equal dimensions to add"
        else:
            # add if correct dimensions
            res = matrix([[]])
            res.zero(self.dimx, self.dimy)
            for i in range(self.dimx):
                for j in range(self.dimy):
                    res.value[i][j] = self.value[i][j] + other.value[i][j]
            return res
    
    def __sub__(self, other):
        # check if correct dimensions
        if self.dimx != other.dimx or self.dimy != other.dimy:
            raise ValueError, "Matrices must be of equal dimensions to subtract"
        else:
            # subtract if correct dimensions
            res = matrix([[]])
            res.zero(self.dimx, self.dimy)
            for i in range(self.dimx):
                for j in range(self.dimy):
                    res.value[i][j] = self.value[i][j] - other.value[i][j]
            return res
    
    def __mul__(self, other):
        # check if correct dimensions
        if self.dimy != other.dimx:
            raise ValueError, "Matrices must be m*n and n*p to multiply"
        else:
            # multiply if correct dimensions
            res = matrix([[]])
            res.zero(self.dimx, other.dimy)
            for i in range(self.dimx):
                for j in range(other.dimy):
                    for k in range(self.dimy):
                        res.value[i][j] += self.value[i][k] * other.value[k][j]
            return res
    
    def transpose(self):
        # compute transpose
        res = matrix([[]])
        res.zero(self.dimy, self.dimx)
        for i in range(self.dimx):
            for j in range(self.dimy):
                res.value[j][i] = self.value[i][j]
        return res
    
    # Thanks to Ernesto P. Adorio for use of Cholesky and CholeskyInverse functions
    
    def Cholesky(self, ztol=1.0e-5):
        # Computes the upper triangular Cholesky factorization of
        # a positive definite matrix.
        res = matrix([[]])
        res.zero(self.dimx, self.dimx)
        
        for i in range(self.dimx):
            S = sum([(res.value[k][i])**2 for k in range(i)])
            d = self.value[i][i] - S
            if abs(d) < ztol:
                res.value[i][i] = 0.0
            else:
                if d < 0.0:
                    raise ValueError, "Matrix not positive-definite"
                res.value[i][i] = np.sqrt(d)
            for j in range(i+1, self.dimx):
                S = sum([res.value[k][i] * res.value[k][j] for k in range(self.dimx)])
                if abs(S) < ztol:
                    S = 0.0
                res.value[i][j] = (self.value[i][j] - S)/res.value[i][i]
        return res
    
    def CholeskyInverse(self):
        # Computes inverse of matrix given its Cholesky upper Triangular
        # decomposition of matrix.
        res = matrix([[]])
        res.zero(self.dimx, self.dimx)
        
        # Backward step for inverse.
        for j in reversed(range(self.dimx)):
            tjj = self.value[j][j]
            S = sum([self.value[j][k]*res.value[j][k] for k in range(j+1, self.dimx)])
            res.value[j][j] = 1.0/tjj**2 - S/tjj
            for i in reversed(range(j)):
                res.value[j][i] = res.value[i][j] = -sum([self.value[i][k]*res.value[k][j] for k in range(i+1, self.dimx)])/self.value[i][i]
        return res
    
    def inverse(self):
        aux = self.Cholesky()
        res = aux.CholeskyInverse()
        return res
    
    def __repr__(self):
        return repr(self.value)

#------------------------------------------ Extended Kalman filter function ----------------------------------------------------------------#
def EKF(x,P,lines,measurements,resolution,count=0):
    count = 0
    I = matrix([[1., 0.], [0., 1.]]) # identity matrix
    #for x1,y1,m1,c1,d1,l1 in lines:
    for x1,y1 in lines:
        theta = np.arctan2(measurements.value[1][0] - y1, measurements.value[0][0] - x1) # angle b/w measured vp and detected lines
        h_theta = np.arctan2((x.value[1][0] - y1),(x.value[0][0] - x1)) # angle between current state and detected lines 
        y = theta - h_theta # difference b/w measured and state angle
        d_square = np.square(x.value[0][0] - x1) + np.square(x.value[1][0] - y1)
        H = matrix([[-(x.value[1][0] - y1)/d_square, (x.value[0][0] - x1)/d_square]])
        omega = abs(measurements.value[0][0] - x.value[0][0])
        if omega > 3:
            factor = (omega/3.0 * np.pi) % (np.pi - 0.01)
            R = matrix([[factor**2 + 0.01]])
        else:
            R = matrix([[0.01]])
        if count < 5:
            if abs(y) < (1):   # diff is < 1 radian (57 degrees)
                count+= 1
                S = H*P*H.transpose() +  R
                K = P*H.transpose()*S.inverse()
                y = matrix([[y]])
                x = x + K*y
                P = (I - K*H)*P
            else:
                #P = matrix([[1250., 0.], [0., 1250.]])
                P = matrix([[16000., 0.], [0., 16000.]])
        else:
            if abs(y) < (.2):
                count+= 1
                S = H*P*H.transpose() +  R
                #print 'S = {0}'.format(S)
                K = P*H.transpose()*S.inverse()
                #y = (np.pi/180 * y)
                y = matrix([[y]])
                x = x + K*y
                P = (I - K*H)*P
            else:
                #P = matrix([[1250., 0.], [0., 1250.]])
                P = matrix([[10000., 0.], [0., 10000.]])
    return x,P

