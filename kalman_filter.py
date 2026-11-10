import numpy as np

# TODO Part 3: Comment the code explaining each part
class kalman_filter:
    
    # DONE: Part 3: Initialize the covariances and the states    
    def __init__(self, P,Q,R, x, dt):
        
        self.P=...
        self.Q=...
        self.R=...
        self.x=...
        self.dt = ...
        
    # DONE: Part 3: Replace the matrices with Jacobians where needed        
    def predict(self):

        self.A = ...
        self.C = ...
        
        self.motion_model()
        
        self.P= np.dot( np.dot(self.A, self.P), self.A.T) + self.Q

    # DONE: Part 3: Calculate the Kalman gain and correct your estimates
    def update(self, z):
        
        kalman_gain= ...
        
        self.x= ...
        
        self.P= ...
        
    
    # DONE: Part 3: Implement here the measurement model
    def measurement_model(self):
        x, y, th, w, v, vdot = self.x
        return np.array([
            v,      # v
            w,      # w
            vdot,   # ax = d/dt(v * cos(theta)) [small angle approximation] = vdot
            v * w,      # ay = d/dt(v * sin(theta)) [small angle approximation] = v*w
        ])
        
    # DONE: Part 3: Impelment the motion model (state-transition matrice)
    def motion_model(self):
        
        x, y, th, w, v, vdot = self.x
        dt = self.dt
        
        self.x = np.array([
            x + v * np.cos(th) * dt,    # x  (updating the x position with np.cos(theta)*dt)
            y + v * np.sin(th) * dt,    # y  (updating the y position with np.sin(theta)*dt)
            th + w * dt,                # th (updating theta with w*dt)
            w,                          # w 
            v  + vdot*dt,               # v  (updating the velocity with the vdot*dt)
            vdot,                       # vdot
        ])

    # DONE: Jacobian A (G_k from the tutorial)
    def jacobian_A(self):
        x, y, th, w, v, vdot = self.x
        dt = self.dt
        return np.array([
            # x,        y,                 th,      w,              v,   vdot
            [1,         0,   -v*np.sin(th)*dt,      0,  np.cos(th)*dt,      0],     # x
            [0,         1,    v*np.cos(th)*dt,      0,  np.sin(th)*dt,      0],     # y
            [0,         0,                  1,      dt,             0,      0],     # th
            [0,         0,                  0,      1,              0,      0],     # w
            [0,         0,                  0,      0,              1,     dt],     # v
            [0,         0,                  0,      0,              0,      1]      # vdot
        ])
    
    
    # DONE: Part 3: Implement here the jacobian of the H matrix (measurements)    
    def jacobian_H(self):
        x, y, th, w, v, vdot=self.x
        return np.array([
            #x, y, th,  w, v, vdot
            [0, 0,  0,  0, 1,   0],   # v
            [0, 0,  0,  1, 0,   0],   # w
            [0, 0,  0,  0, 0,   1],   # ax = vdot 
            [0, 0,  0,  1, 1,   0],   # ay = v * w
        ])
        
    # DONE: Part 3: return the states here    
    def get_states(self):
        return self.x
