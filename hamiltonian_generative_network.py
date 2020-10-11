import torch

from networks.inference_net import EncoderNet, TransformerNet
from networks.hamiltonian_net import HamiltonianNet
from utils.integrator import Integrator
from utils.hgn_result import HgnResult


class HGN():
    """Hamiltonian Generative Network model.
    
    This class models the HGN and allows implements its training and evaluation.
    """
    def __init__(self,
                 encoder,
                 transformer,
                 hnn,
                 decoder,
                 integrator,
                 optimizer,
                 loss,
                 seq_len,
                 channels=3):
        # Parameters
        self.seq_len = seq_len
        self.channels = channels

        # Modules
        self.encoder = encoder
        self.transformer = transformer
        self.hnn = hnn
        self.decoder = decoder
        self.integrator = integrator

        # Optimization
        self.optimizer = optimizer
        self.loss = loss

    def forward(self, rollout, steps=None):
        assert (rollout.size()[1] == self.channels * self.seq_len
                )  # Rollout channel dim needs to be 3*seq_len
        steps = self.seq_len if steps is None else steps  # If steps not specified, match input sequence length

        prediction = HgnResult()
        prediction.set_input(rollout)

        # Latent distribution
        z, z_mean, z_std = self.encoder(rollout)
        prediction.set_z(z_mean=z_mean, z_std=z_std, z_sample=z)

        # Initial state
        q, p = self.transformer(prediction.z_sampled)
        prediction.append_state(q=q, p=p)

        # Initial state reconstruction
        x_reconstructed = self.decoder(q=q)
        prediction.append_reconstruction(x_reconstructed)

        # Estimate predictions
        q.requires_grad = True  # We will need dH/dq
        p.requires_grad = True  # We will need dh/dp
        for _ in range(steps):
            # Compute next state
            q, p = self.integrator.step(q=q, p=p, hnn=self.hnn)
            prediction.append_state(q=q, p=p)

            # Compute state reconstruction
            x_reconstructed = self.decoder(q=q)
            prediction.append_reconstruction(x_reconstructed)
        return prediction

    def fit(self, rollouts, loss):
        self.optimizer.zero_grad()
        prediction = self.forward(rollout=rollouts)
        error = self.loss(input=prediction.input,
                          target=prediction.reconstructed_rollout)
        error.backward()
        optimizer.step()

    def load(self, file_name):
        raise NotImplementedError

    def save(self, file_name):
        raise NotImplementedError


if __name__ == "__main__":
    seq_len = 10
    integrator = Integrator(delta_T=0.1, method="euler")

    hgn = HGN(seq_len=seq_len, integrator=integrator)