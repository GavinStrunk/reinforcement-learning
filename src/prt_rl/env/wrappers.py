import gymnasium as gym
from tensordict.tensordict import TensorDict
import torch
from typing import Optional, Tuple
from prt_sim.jhu.base import BaseEnvironment
from prt_rl.env.interface import EnvironmentInterface, EnvParams

class JhuWrapper(EnvironmentInterface):
    """
    Wraps the JHU environments in the Environment interface.

    The JHU environments are games and puzzles that were used in the JHU 705.741 RL course.
    """
    def __init__(self,
                 environment: BaseEnvironment,
                 render_mode: Optional[str] = None,
                 ) -> None:
        super().__init__(render_mode)
        self.env = environment

    def get_parameters(self) -> EnvParams:
        params = EnvParams(
            action_shape=(1,),
            action_continuous=False,
            action_min=0,
            action_max=self.env.get_number_of_actions()-1,
            observation_shape=(1,),
            observation_continuous=False,
            observation_min=0,
            observation_max=max(self.env.get_number_of_states()-1, 0),
        )
        return params

    def reset(self) -> TensorDict:
        state = self.env.reset()
        state_td = TensorDict(
            {
                'observation': torch.tensor([[state]], dtype=torch.int),
            },
            batch_size=torch.Size([1])
        )

        if self.render_mode is not None:
            self.env.render()

        return state_td

    def step(self, action: TensorDict) -> TensorDict:
        action_val = action['action'][0].item()
        state, reward, done = self.env.execute_action(action_val)
        action['next'] = {
            'observation': torch.tensor([[state]], dtype=torch.int),
            'reward': torch.tensor([[reward]], dtype=torch.float),
            'done': torch.tensor([[done]], dtype=torch.bool),
        }

        if self.render_mode is not None:
            self.env.render()

        return action

class GymnasiumWrapper(EnvironmentInterface):
    """
    Wraps the Gymnasium environments in the Environment interface.

    """
    def __init__(self,
                 gym_name: str,
                 render_mode: Optional[str] = None,
                 ) -> None:
        super().__init__(render_mode)
        self.gym_name = gym_name
        self.env = gym.make(self.gym_name, render_mode=render_mode)

    def get_parameters(self) -> EnvParams:
        if isinstance(self.env.action_space, gym.spaces.Discrete):
            act_shape, act_cont, act_min, act_max = self._get_params_from_discrete(self.env.action_space)
        else:
            raise NotImplementedError("Only discrete action spaces are supported")

        if isinstance(self.env.observation_space, gym.spaces.Discrete):
            obs_shape, obs_cont, obs_min, obs_max = self._get_params_from_discrete(self.env.observation_space)
        else:
            raise NotImplementedError("Only discrete observation spaces are supported")

        return EnvParams(
            action_shape=act_shape,
            action_continuous=act_cont,
            action_min=act_min,
            action_max=act_max,
            observation_shape=obs_shape,
            observation_continuous=obs_cont,
            observation_min=obs_min,
            observation_max=obs_max,
        )

    def reset(self) -> TensorDict:
        obs, info = self.env.reset()

        state_td = TensorDict(
            {
                'observation': torch.tensor([[obs]], dtype=torch.int),
            },
            batch_size=torch.Size([1])
        )
        return state_td

    def step(self, action: TensorDict) -> TensorDict:
        action_val = action['action'][0].item()
        state, reward, terminated, trunc, info = self.env.step(action_val)
        done = terminated or trunc
        action['next'] = {
            'observation': torch.tensor([[state]], dtype=torch.int),
            'reward': torch.tensor([[reward]], dtype=torch.float),
            'done': torch.tensor([[done]], dtype=torch.bool),
        }

        return action

    @staticmethod
    def _get_params_from_discrete(space: gym.spaces.Discrete) -> Tuple[tuple, bool, int, int]:
        """
        Extracts the environment parameters from a discrete space.

        Args:
            space (gym.spaces.Discrete): The space to extract parameters from.

        Returns:
            Tuple[tuple, bool, int, int]: tuple containing (space_shape, space_continuous, space_min, space_max)
        """
        return (1,), False, space.start, space.n - 1