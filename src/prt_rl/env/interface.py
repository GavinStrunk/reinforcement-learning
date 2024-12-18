from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

from tensordict import tensordict

@dataclass
class EnvParams:
    """
    Environment parameters contains information about the action and observation spaces to configure RL algorithms.

    Parameters:
        action_shape (tuple): shape of the action space
        action_continuous (bool): True if the actions are continuous or False if they are discrete
        action_min: Minimum action value. If this is a scalar it is applied to all actions otherwise it must match the action shape
        action_max: Maximum action values. If this is a scalar it is applied to all actions otherwise it must match the action shape
        observation_shape (tuple): shape of the observation space
        observation_continuous (bool): True if the observations are continuous or False if they are discrete
        observation_min: Minimum observation value. If this is a scalar it is applied to all observations otherwise it must match the observation shape
        observation_max: Maximum observation value. If this is a scalar it is applied to all observations otherwise it must match the observation shape
    """
    action_shape: tuple
    action_continuous: bool
    action_min: Union[int, float]
    action_max: Union[int, float]
    observation_shape: tuple
    observation_continuous: bool
    observation_min: Union[int, float]
    observation_max: Union[int, float]

@dataclass
class MultiAgentEnvParams:
    """
    Multi-Agent environment parameters contains information about the action and observation spaces to configure multi-agent RL algorithms.

    Notes:
        This is still a work in progress.

    group = {
    name: (num_agents, EnvParams)
    }
    """
    group: dict

class EnvironmentInterface(ABC):
    """
    The environment interface wraps other simulation environments to provide a consistent interface for the RL library.

    The interface for agents is based around tensordicts. Dictionaries are used in many of the common RL libraries such as: RLlib, TorchRL, and Tianshou. I believe they have all converged to the same type of interface because it provides the most flexibility. However, care needs to be taken to ensure keys are consistent otherwise dictionaries are a free for all.

    Single Agent Interface
    For a single agent the tensordict trajectory has the following structure:
    {
        "observation": tensor,
        "action": tensor,
        "next":
        {
            "observation": tensor,
            "reward": tensor,
            "done": tensor,
            "info": dict,
        }
    }
    The shape of each tensor is (N, M) where N is the number of environments and M is the size of the value. For example, if an agent has two output actions and we are training with four environments then the "action" key will have shape (4,2).

    """
    @abstractmethod
    def get_parameters(self) -> EnvParams:
        """
        Returns the EnvParams object which contains information about the sizes of observations and actions needed for setting up RL agents.

        Returns:
            EnvParams: environment parameters object
        """
        raise NotImplementedError()

    @abstractmethod
    def reset(self) -> tensordict:
        """
        Resets the environment to the initial state and returns the initial observation.

        Returns:
            tensordict: initial observation
        """
        raise NotImplementedError()

    @abstractmethod
    def step(self, action: tensordict) -> tensordict:
        """
        Steps the simulation using the "action" key in the tensordict and returns the new trajectory.

        Args:
            action (tensordict): Tensordict with "action" key that is a tensor with shape (# env, # actions)

        Returns:
            tensordict: Tensordict trajectory with the "next" key
        """
        raise NotImplementedError()