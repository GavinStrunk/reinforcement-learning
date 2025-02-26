import flappy_bird_gymnasium
import numpy as np
import pytest
import torch
import vmas
from prt_rl.env import wrappers
from prt_rl.env.interface import MultiAgentEnvParams, MultiGroupEnvParams
from prt_sim.jhu.bandits import KArmBandits
from prt_sim.jhu.robot_game import RobotGame

def test_jhu_wrapper_for_bandits():
    env = wrappers.JhuWrapper(environment=KArmBandits())

    # Check the EnvParams are filled out correctly
    params = env.get_parameters()
    assert params.action_shape == (1,)
    assert params.action_continuous == False
    assert params.action_min == 0
    assert params.action_max == 9
    assert params.observation_shape == (1,)
    assert params.observation_continuous == False
    assert params.observation_min == 0
    assert params.observation_max == 0

    # Check interface
    state_td = env.reset()
    assert state_td.shape == (1,)
    assert state_td['observation'].shape == (1, *params.observation_shape)

    action = state_td
    action['action'] = torch.tensor([[0]])
    trajectory_td = env.step(action)
    print(trajectory_td)

def test_jhu_wrapper_for_robot_game():
    env = wrappers.JhuWrapper(environment=RobotGame())

    # Check the EnvParams are filled out correctly
    params = env.get_parameters()
    assert params.action_shape == (1,)
    assert params.action_continuous == False
    assert params.action_min == 0
    assert params.action_max == 3
    assert params.observation_shape == (1,)
    assert params.observation_continuous == False
    assert params.observation_min == 0
    assert params.observation_max == 10

    # Check interface
    state_td = env.reset()
    assert state_td.shape == (1,)
    assert state_td['observation'].shape == (1, *params.observation_shape)

    action = state_td
    action['action'] = torch.tensor([[0]])
    trajectory_td = env.step(action)
    print(trajectory_td)

def test_gymnasium_wrapper_for_cliff_walking():
    # Reference: https://gymnasium.farama.org/environments/toy_text/cliff_walking/
    env = wrappers.GymnasiumWrapper(
        gym_name="CliffWalking-v0"
    )

    params = env.get_parameters()
    assert params.action_shape == (1,)
    assert params.action_continuous == False
    assert params.action_min == 0
    assert params.action_max == 3
    assert params.observation_shape == (1,)
    assert params.observation_continuous == False
    assert params.observation_min == 0
    assert params.observation_max == 47

    state_td = env.reset()
    assert state_td.shape == (1,)
    assert state_td['observation'].shape == (1, *params.observation_shape)
    assert state_td['observation'].dtype == torch.int64

    action = state_td
    action['action'] = torch.tensor([[0]])
    trajectory_td = env.step(action)
    print(trajectory_td)

def test_gymnasium_wrapper_continuous_observations():
    env = wrappers.GymnasiumWrapper(
        gym_name="FlappyBird-v0",
        render_mode=None,
        use_lidar=False,
        normalize_obs=True
    )

    params = env.get_parameters()
    assert params.action_shape == (1,)
    assert params.action_continuous == False
    assert params.action_min == 0
    assert params.action_max == 1
    assert params.observation_shape == (12,)
    assert params.observation_continuous == True
    assert len(params.observation_min) == 12
    assert all(omin == -1 for omin in params.observation_min)
    assert len(params.observation_max) == 12
    assert all(omax == 1 for omax in params.observation_max)

    state_td = env.reset()
    assert state_td.shape == (1,)
    assert state_td['observation'].shape == (1, *params.observation_shape)
    assert state_td['observation'].dtype == torch.float64

    action = state_td
    action['action'] = torch.zeros(1, *params.action_shape)
    trajectory_td = env.step(action)
    assert trajectory_td.shape == (1,)
    assert trajectory_td['next', 'reward'].shape == (1, 1)
    assert trajectory_td['next', 'done'].shape == (1, 1)

def test_gymnasium_wrapper_continuous_actions():
    env = wrappers.GymnasiumWrapper(
        gym_name="MountainCarContinuous-v0",
        render_mode=None,
    )

    params = env.get_parameters()
    assert params.action_shape == (1,)
    assert params.action_continuous == True
    assert params.action_min == [-1]
    assert params.action_max == [1.0]
    assert params.observation_shape == (2,)
    assert params.observation_continuous == True
    assert params.observation_min == pytest.approx([-1.2, -0.07])
    assert params.observation_max == pytest.approx([0.6, 0.07])

    state_td = env.reset()
    assert state_td.shape == (1,)
    assert state_td['observation'].shape == (1, *params.observation_shape)
    assert state_td['observation'].dtype == torch.float32

    action = state_td
    action['action'] = torch.zeros(1, *params.action_shape)
    trajectory_td = env.step(action)
    assert trajectory_td.shape == (1,)
    assert trajectory_td['next', 'reward'].shape == (1, 1)
    assert trajectory_td['next', 'done'].shape == (1, 1)

def test_vmas_wrapper():
    num_envs = 2
    env = wrappers.VmasWrapper(
        scenario="discovery",
        num_envs=num_envs,
    )

    assert isinstance(env.env, vmas.simulator.environment.environment.Environment)

    params = env.get_parameters()
    assert isinstance(params, MultiAgentEnvParams)
    assert params.num_agents == 5
    assert params.agent.action_shape == (2,)
    assert params.agent.action_continuous == True
    assert params.agent.action_min == [-1.0, -1.0]
    assert params.agent.action_max == [1.0, 1.0]
    assert params.agent.observation_shape == (19,)
    assert params.agent.observation_continuous == True
    assert params.agent.observation_min == [-np.inf]*19
    assert params.agent.observation_max == [np.inf]*19

    state_td = env.reset()
    assert state_td.shape == (num_envs,)
    assert state_td['observation'].shape == (num_envs, params.num_agents, *params.agent.observation_shape)
    assert state_td['observation'].dtype == torch.float32

    action = state_td
    action['action'] = torch.zeros(num_envs, params.num_agents, *params.agent.action_shape)
    trajectory_td = env.step(action)
    assert trajectory_td.shape == (num_envs,)
    assert trajectory_td['next', 'reward'].shape == (num_envs, params.num_agents)
    assert trajectory_td['next', 'done'].shape == (num_envs, 1)

def test_multigroup_vmas_wrapper():
    num_envs = 1
    env = wrappers.VmasWrapper(
        scenario="kinematic_bicycle",
        num_envs=num_envs,
    )

    assert isinstance(env.env, vmas.simulator.environment.environment.Environment)

    params = env.get_parameters()
    assert isinstance(params, MultiGroupEnvParams)
    assert list(params.group.keys()) == ['bicycle', 'holo_rot']

    ma_bike = params.group['bicycle']
    assert ma_bike.num_agents == 1
    assert ma_bike.agent.action_shape == (2,)
    assert ma_bike.agent.action_continuous == True
    assert ma_bike.agent.action_min == [-1.0, -0.5235987901687622]
    assert ma_bike.agent.action_max == [1.0, 0.5235987901687622]
    assert ma_bike.agent.observation_shape == (4,)
    assert ma_bike.agent.observation_continuous == True
    assert ma_bike.agent.observation_min == [-np.inf]*4
    assert ma_bike.agent.observation_max == [np.inf]*4

    ma_holo = params.group['holo_rot']
    assert ma_holo.num_agents == 1
    assert ma_holo.agent.action_shape == (3,)
    assert ma_holo.agent.action_continuous == True
    assert ma_holo.agent.action_min == [-1.0, -1.0, -1.0]
    assert ma_holo.agent.action_max == [1.0, 1.0, 1.0]
    assert ma_holo.agent.observation_shape == (4,)
    assert ma_holo.agent.observation_continuous == True
    assert ma_holo.agent.observation_min == [-np.inf]*4
    assert ma_holo.agent.observation_max == [np.inf]*4
