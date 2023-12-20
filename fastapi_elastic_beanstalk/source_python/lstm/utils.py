import numpy as np
import matplotlib.pyplot as plt
import torch
from .lstm_encoder_decoder import lstm_seq2seq

class RateStateModel:
    """ 
    Class for rate and state model 
    """

    def reduced_order_model_evaluate(self,lstm_model):

        def get_acc_for_current_step(step_number, window, t):
            start                  = step_number * window
            end                    = start + window
            train_plt[0:window, 0] = t[start:end, 0]
            train_plt[0:window, 1] = t[start:end, 1]
            train_plt_torch        = torch.from_numpy(train_plt).type(torch.Tensor)
            Y_train_pred           = lstm_model.predict(train_plt_torch, target_len=window)
            acc[start:end, 0]      = Y_train_pred[:, 0]
            acc[start:end, 1]      = Y_train_pred[:, 0]
            return acc 
                
        # Calculate the number of steps to take
        num_steps   = int(np.floor((self.t_final - self.t_start) / self.delta_t))
        window      = int(self.num_tsteps/20)
        # Create arrays to store trajectory
        t           = np.zeros((num_steps, 2))
        acc         = np.zeros((num_steps, 2))
        t[0, 0]     = self.t_start
        # Calculate the time array
        k = 1
        while k < num_steps:
            t[k, 0] = t[k-1, 0] + self.delta_t
            k += 1
        t[:, 1]     = self.Dc
        num_steps   = int(num_steps / window)
        train_plt   = np.zeros((window, 2))

        # Predict acceleration using the LSTM model
        for step_number in range(num_steps):
            acc     = get_acc_for_current_step(step_number, window, t)

        # Return the time and acceleration arrays
        return t, acc

class RSF:
   """
   Driver class for RSF model
   """

   def _create_training_sequences(self, data, T, window, stride):
      """
      Create training sequences for the LSTM model.
      """

      n_train = (data.shape[0] - window) // stride + 1
      Y_train = np.zeros([window, n_train, self.num_features])
      T_train = np.zeros([window, n_train, self.num_features])

      for feature_index in range(self.num_features):
         for i in range(n_train):
            start, end = stride * i, stride * i + window
            Y_train[:, i, feature_index] = data[start:end, feature_index]
            T_train[:, i, feature_index] = T[start:end, feature_index]

      Y_train_torch = torch.from_numpy(Y_train).type(torch.Tensor)
      T_train_torch = torch.from_numpy(T_train).type(torch.Tensor)
      
      return n_train, Y_train_torch, T_train_torch
         
   def build_lstm(self, epochs=20, num_layers=1, batch_size=1):
      """
      Build and train an LSTM model.
      """

      window  = int(self.model.num_tsteps/20)
      stride  = int(window/5)
      T       = self.t_appended.reshape(-1,self.num_features)
      data    = self.acc_appended.reshape(-1,self.num_features)
      
      # Generate the sequences for training
      n_train, Y_train, T_train = self._create_training_sequences(data, T, window, stride)

      # Define the parameters for the LSTM model      
      hidden_size  = window
      lstm_model = lstm_seq2seq(T_train.shape[2], hidden_size, num_layers)

      # Train the model
      _ = lstm_model.train_model(T_train, Y_train, epochs, window, batch_size)

      # Plot the results of the trained LSTM model
      self.plot_lstm(n_train, window, stride, T_train.numpy(), Y_train.numpy(), lstm_model)

      return lstm_model

   def initialize_arrays(self, n_train, window):
      """
      Initialize arrays for target, input, and output signals.

      Returns:
      Tuple of numpy.ndarrays: Initialized arrays X, Y, T.
      """

      array_size = int(n_train * window / self.num_dc)
      return (np.zeros(array_size), np.zeros(array_size), np.zeros(array_size))

   def plot_signals(self, T, X, Y, dc):
      """
      Plot the target and predicted output signals.

      Parameters:
      T (numpy.ndarray): Time data.
      X (numpy.ndarray): Target signal data.
      Y (numpy.ndarray): Predicted signal data.
      dc (float): Displacement current.
      """

      plt.figure()
      plt.plot(T, X, '-', linewidth=1.0, markersize=1.0, label='Target')
      plt.plot(T, Y, '-', linewidth=1.0, markersize=1.0, label='Predicted')
      plt.xlabel('Time (sec)')
      plt.ylabel('a (μm/s²)')
      plt.legend(frameon=False)
      plt.suptitle(f'Training data set for dc={dc} μm')
      plt.tight_layout()
      plt.show()

   def plot_lstm(self, n_train, window, stride, Ttrain, Ytrain, lstm_model):
      """
      Plot the results of the trained LSTM model.

      Parameters:
      n_train (int): Number of training samples.
      window (int): Window size for LSTM.
      stride (int): Stride for window.
      Ttrain (numpy.ndarray): Training time data.
      Ytrain (numpy.ndarray): Training target data.
      lstm_model (Model): Trained LSTM model.
      """

      plt.rcParams.update({'font.size': 10})
      count_dc = 0

      for dc in self.dc_list:
         num_samples_per_dc = int(n_train / self.num_dc)
         X, Y, T            = self.initialize_arrays(n_train, window, num_samples_per_dc)
         for sample_number in range(num_samples_per_dc):
            start           = sample_number * stride
            end             = start + window
            train_plt       = Ttrain[:, count_dc * num_samples_per_dc + sample_number, :]
            train_plt_torch = torch.from_numpy(train_plt).type(torch.Tensor)
            Y_train_pred    = lstm_model.predict(train_plt_torch, target_len=window)
            X[start:end]    = Ytrain[:, count_dc * num_samples_per_dc + sample_number, 0]
            Y[start:end]    = Y_train_pred[:, 0]
            T[start:end]    = Ttrain[:, count_dc * num_samples_per_dc + sample_number, 0]

         self.plot_signals(T, X, Y, dc)
         count_dc += 1
         del X, Y, T


def plot_lstm_predictions(model, Ttrain, Ytrain, Ttest, Ytest, num_rows=4):
    """
    Plot predictions of the LSTM encoder-decoder on training and test data.

    Parameters:
    model (torch.nn.Module): Trained LSTM encoder-decoder model.
    Ttrain, Ttest (np.array): Time arrays for training and test data.
    Ytrain, Ytest (np.array): Target data arrays for training and test data.
    num_rows (int): Number of rows of plots to display.

    Returns:
    None: Plots are displayed and saved to a file.
    """

    # Validate input arrays
    if not (Ttrain.ndim == Ttest.ndim == Ytrain.ndim == Ytest.ndim == 2):
        raise ValueError("Input arrays must be 2-dimensional.")

    # Prepare figure for plotting
    fig, axes = plt.subplots(num_rows, 2, figsize=(13, 15))
    fig.suptitle('LSTM Encoder-Decoder Predictions', x=0.445, y=1.)
    
    for i in range(num_rows):
        for j, (T, Y, title) in enumerate([(Ttrain, Ytrain, 'Train'), (Ttest, Ytest, 'Test')]):
            # Validate array dimensions
            if T.shape[0] != Y.shape[0]:
                raise ValueError("Time and data arrays must have the same length.")

            # Select data for plotting
            t = T[:, i] if T.shape[1] > i else T[:, 0]
            y_true = Y[:, i] if Y.shape[1] > i else Y[:, 0]
            
            # Generate model predictions
            y_pred = model.predict(torch.from_numpy(y_true[np.newaxis, :, np.newaxis]).type(torch.Tensor)).squeeze().numpy()

            # Plot data
            ax = axes[i, j]
            ax.plot(t, y_true, color=(0.2, 0.42, 0.72), label='Target')
            ax.plot(t, y_pred, color=(0.76, 0.01, 0.01), label='Prediction')
            ax.set_xlabel('$Time (sec)$')
            ax.set_ylabel('$a (\mu m/s^2)$')
            ax.set_title(title)
            if i == 0 and j == 1:
                ax.legend(bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    plt.savefig('plots/predictions.png')
    plt.show()

