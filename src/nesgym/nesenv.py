#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By Lilian Besson (Naereen)
# https://github.com/Naereen/gym-nes-mario-bros
# MIT License https://lbesson.mit-license.org/
#
from __future__ import division, print_function  # Python 2 compatibility

import os
import os.path
import subprocess
import sys
import struct


# USE_MULTIPROCESS = False
# if USE_MULTIPROCESS:
#     from multiprocessing import Process as Thread, Condition
from threading import Thread, Condition

import numpy as np
from PIL import Image

import gym
from gym.envs.classic_control import rendering
from gym import utils, spaces
from gym.utils import seeding

package_directory = os.path.dirname(os.path.abspath(__file__))
SEP = '|'

_pipenumber_filename = "/tmp/nesgym-pipe-number.txt"

# NES palette, 128 colors (7 bits for colors)
rgb = {
    '00': (116, 116, 116),
    '01': (36, 24, 140),
    '02': (0, 0, 168),
    '03': (68, 0, 156),
    '04': (140, 0, 116),
    '05': (168, 0, 16),
    '06': (164, 0, 0),
    '07': (124, 8, 0),
    '08': (64, 44, 0),
    '09': (0, 68, 0),
    '0A': (0, 80, 0),
    '0B': (0, 60, 20),
    '0C': (24, 60, 92),
    '0D': (0, 0, 0),
    '0E': (0, 0, 0),
    '0F': (0, 0, 0),
    '10': (188, 188, 188),
    '11': (0, 112, 236),
    '12': (32, 56, 236),
    '13': (128, 0, 240),
    '14': (188, 0, 188),
    '15': (228, 0, 88),
    '16': (216, 40, 0),
    '17': (200, 76, 12),
    '18': (136, 112, 0),
    '19': (0, 148, 0),
    '1A': (0, 168, 0),
    '1B': (0, 144, 56),
    '1C': (0, 128, 136),
    '1D': (0, 0, 0),
    '1E': (0, 0, 0),
    '1F': (0, 0, 0),
    '20': (252, 252, 252),
    '21': (60, 188, 252),
    '22': (92, 148, 252),
    '23': (204, 136, 252),
    '24': (244, 120, 252),
    '25': (252, 116, 180),
    '26': (252, 116, 96),
    '27': (252, 152, 56),
    '28': (240, 188, 60),
    '29': (128, 208, 16),
    '2A': (76, 220, 72),
    '2B': (88, 248, 152),
    '2C': (0, 232, 216),
    '2D': (120, 120, 120),
    '2E': (0, 0, 0),
    '2F': (0, 0, 0),
    '30': (252, 252, 252),
    '31': (168, 228, 252),
    '32': (196, 212, 252),
    '33': (212, 200, 252),
    '34': (252, 196, 252),
    '35': (252, 196, 216),
    '36': (252, 188, 176),
    '37': (252, 216, 168),
    '38': (252, 228, 160),
    '39': (224, 252, 160),
    '3A': (168, 240, 188),
    '3B': (176, 252, 204),
    '3C': (156, 252, 240),
    '3D': (196, 196, 196),
    '3E': (0, 0, 0),
    '3F': (0, 0, 0),
    '40': (87, 87, 87),
    '41': (27, 18, 105),
    '42': (0, 0, 126),
    '43': (51, 0, 117),
    '44': (105, 0, 87),
    '45': (126, 0, 12),
    '46': (123, 0, 0),
    '47': (93, 6, 0),
    '48': (48, 33, 0),
    '49': (0, 51, 0),
    '4A': (0, 60, 0),
    '4B': (0, 45, 15),
    '4C': (18, 45, 69),
    '4D': (0, 0, 0),
    '4E': (0, 0, 0),
    '4F': (0, 0, 0),
    '50': (141, 141, 141),
    '51': (0, 84, 177),
    '52': (24, 42, 177),
    '53': (96, 0, 180),
    '54': (141, 0, 141),
    '55': (171, 0, 66),
    '56': (162, 30, 0),
    '57': (150, 57, 9),
    '58': (102, 84, 0),
    '59': (0, 111, 0),
    '5A': (0, 126, 0),
    '5B': (0, 108, 42),
    '5C': (0, 96, 102),
    '5D': (0, 0, 0),
    '5E': (0, 0, 0),
    '5F': (0, 0, 0),
    '60': (189, 189, 189),
    '61': (45, 141, 189),
    '62': (69, 111, 189),
    '63': (153, 102, 189),
    '64': (183, 90, 189),
    '65': (189, 87, 135),
    '66': (189, 87, 72),
    '67': (189, 114, 42),
    '68': (180, 141, 45),
    '69': (96, 156, 12),
    '6A': (57, 165, 54),
    '6B': (66, 186, 114),
    '6C': (0, 174, 162),
    '6D': (90, 90, 90),
    '6E': (0, 0, 0),
    '6F': (0, 0, 0),
    '70': (189, 189, 189),
    '71': (126, 171, 189),
    '72': (147, 159, 189),
    '73': (159, 150, 189),
    '74': (189, 147, 189),
    '75': (189, 147, 162),
    '76': (189, 141, 132),
    '77': (189, 162, 126),
    '78': (189, 171, 120),
    '79': (168, 189, 120),
    '7A': (126, 180, 141),
    '7B': (132, 189, 153),
    '7C': (117, 189, 180),
    '7D': (147, 147, 147),
    '7E': (0, 0, 0),
    '7F': (0, 0, 0),
}

palette_rgb = np.array([rgb[key] for key in sorted(rgb.keys())])
palette_grayscale = np.array([(0.299*r+0.587*g+0.114*b) / 256.0 for r, g, b in palette_rgb])

SCREEN_WIDTH, SCREEN_HEIGHT = 256, 224

# See https://github.com/Naereen/gym-nes-mario-bros/issues/5
NB_COLORS_SCREEN = 3
NB_COLORS_OBS = 1

# XXX Change here if you want the DQN to learn from the frame and not the difference of successive frame
USE_DIFFERENCE_OF_FRAMES = True
USE_DIFFERENCE_OF_FRAMES = False


class NESEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, **kwargs):
        utils.EzPickle.__init__(self)
        self.curr_seed = 0
        self._emulatornumber = 0
        self._update_emulatornumber()
        print("Info: Using emulator number {} ...".format(self._emulatornumber))  # DEBUG

        self.raw_screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, NB_COLORS_OBS), dtype=np.uint8)
        self.last_screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, NB_COLORS_OBS), dtype=np.uint8)
        self.screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, NB_COLORS_SCREEN), dtype=np.uint8)
        self.closed = False
        self.can_send_command = True
        self.command_cond = Condition()
        self.viewer = None
        self.reward = 0
        self.score = 0
        # Configuration for difference of rewards when you lose a life or win a level
        self.life = 2
        self.delta_reward_by_life = 0
        self.level = 1
        self.delta_reward_by_level = 0

        episode_time_length_secs = 2*960  # 16 minutes is the max time by episode!
        # self.frame_skip = 1
        # self.frame_skip = 2
        self.frame_skip = 4
        # self.frame_skip = 8
        # self.frame_skip = 10

        # XXX 60 if human mode, about 120 if maximum speed
        fps = 60
        # fps = 120
        self.episode_length = episode_time_length_secs * fps / self.frame_skip

        # All the possible actions.  Try to use the smallest
        # possible number of actions in the child class!
        self.actions = [
            'U', 'D', 'L', 'R',  # up, down, left, right
            'UR', 'DR', 'URA', 'DRB',  # up/down+right, up/down+right+a/B
            'UL', 'DL', 'ULA', 'DLB',  # up/down+left, up/down+left+a/B
            'A', 'B',    # a, b
            'RB', 'RA'   # right+b, right+a
            'LB', 'LA',  # left+b, left+a
            'S', 'E'  # start, select
        ]
        self.action_space = spaces.Discrete(len(self.actions))
        self.frame = 0

        # for communication with emulator
        self.pipe_in = None
        self.pipe_out = None
        self.thread_incoming = None

        self.rom_file_path = None
        self.lua_interface_path = None
        self.emulator_started = False

    ## ---------- gym.Env methods -------------
    def _step(self, action):
        self.frame += 1
        done = False
        if self.frame >= self.episode_length:
            done = True
            self.frame = 0
        if USE_DIFFERENCE_OF_FRAMES:
            # WARNING Use difference of consecutive screens instead of just the screen
            obs = self.raw_screen[:] - self.last_screen[:]
            self.last_screen[:] = self.raw_screen[:]
            # DEBUG Use .copy() if this [:] indexing hack don't work
        else:
            obs = self.screen[:]
        info = {
            "frame": self.frame,
            "score": self.score,
            "level": self.level,
            "life": self.life,
        }
        with self.command_cond:
            while not self.can_send_command:
                self.command_cond.wait()
            self.can_send_command = False
        self._joypad(self.actions[action])
        # FIXME hack to give 1 reward if still alive!
        if self.reward == 0:
            self.reward = 1
        # # FIXME hack to change reward if going right
        # if self.actions[action] == 'BR':
        #     self.reward += 100
        return obs, self.reward, done, info

    def _reset(self):
        print("Info: reseting the environment...")  # DEBUG
        if not self.emulator_started:
            self._start_emulator()
        self.reward = 0
        self.score = 0
        self.life = 2
        self.level = 1
        self.screen.fill(0)
        self._write_to_pipe('reset' + SEP)
        with self.command_cond:
            self.can_send_command = False
        return self.screen

    def _load(self):
        print("Info: loading reference state...")  # DEBUG
        if not self.emulator_started:
            self._start_emulator()
        self.reward = 0
        self.score = 0
        self.life = 2
        self.level = 1
        self.screen.fill(0)
        self._write_to_pipe('loadstate' + SEP)
        with self.command_cond:
            self.can_send_command = False
        return self.screen

    def _render(self, mode='human', close=False):
        if mode == 'human':
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(self.screen)
        elif mode == 'rgb_array':
            return self.screen

    def _seed(self, seed=None):
        self.curr_seed = seeding.hash_seed(seed) % 256
        return [self.curr_seed]

    def _close(self):
        self.closed = True
    ## ------------- end gym.Env --------------

    ## ------------- emulator related ------------
    def _start_emulator(self):
        if not self.rom_file_path:
            raise Exception('No rom file specified!')
        if not self.lua_interface_path:
            raise Exception("Must specify a lua interface file to get scores!")

        print("Opening pipes...")
        self._open_pipes()

        print("Starting fceux emulator...")
        args = ['fceux', '--loadlua', self.lua_interface_path, self.rom_file_path, '&']
        proc = subprocess.Popen(' '.join(args), shell=True)
        proc.communicate()
        # FIXME: no matter whether it starts, proc.returncode is always zero
        self.emulator_started = True
        print("Started fceux emulator!")

    def _joypad(self, button):
        self._write_to_pipe('joypad' + SEP + button)
    ## ------------  end emulator  -------------

    ## ------------- pipes ---------------
    def _update_emulatornumber(self):
        nb = self._emulatornumber
        if os.path.exists(_pipenumber_filename):
            with open(_pipenumber_filename, 'r') as f:
                nb = int(f.readline()) + 1
        with open(_pipenumber_filename, 'w') as f:
            f.write(str(nb))
        self._emulatornumber = nb

    def _write_to_pipe(self, message):
        if not self.pipe_out:
            # arg 1 for line buffering - see python doc
            self.pipe_out = open(self.pipe_out_name, 'w', 1)
        self.pipe_out.write(message + '\n')
        self.pipe_out.flush()

    def _pipe_handler(self):
        with open(self.pipe_in_name, 'rb') as pipe:
            while not self.closed:
                msg = pipe.readline()
                body = msg.split(b'\xFF')
                msg_type, frame = body[0], body[1]
                msg_type = msg_type.decode('ascii')
                frame = int(frame.decode('ascii'))
                if msg_type == "wait_for_command":
                    with self.command_cond:
                        self.can_send_command = True
                        self.command_cond.notify_all()  # FIXME not sure what to use here
                        # self.command_cond.notify(1)
                elif msg_type == "screen":
                    screen_pixels = body[2]
                    pvs = np.array(struct.unpack('B'*len(screen_pixels), screen_pixels))
                    # palette values received from lua are offset by 20 to avoid '\n's
                    self.raw_screen = pvs.reshape((SCREEN_HEIGHT, SCREEN_WIDTH, NB_COLORS_OBS))
                    pvs = np.array(palette_rgb[pvs-20], dtype=np.uint8)
                    self.screen = pvs.reshape((SCREEN_HEIGHT, SCREEN_WIDTH, NB_COLORS_SCREEN))
                elif msg_type == "data":
                    # print("(from Python) received data =", body[2])  # DEBUG
                    # XXX new format is %02x%06i%02x%02x", reward, score, life, level
                    # print("body =", body)  # DEBUG
                    self.reward = int(body[2][:2], 16)
                    # print("(from Python) self.reward =", self.reward)  # DEBUG
                    # print(body[2][3:9])  # DEBUG
                    # print("(from Python) score =", self.score)  # DEBUG
                    self.score = int(body[2][3:9])
                    # print("(from Python) life =", body[2][10:12])  # DEBUG
                    life = body[2][10:12]
                    if len(life) > 0:
                        life = int(body[2][10:12], 16)
                    else:
                        life = 0
                    if life != self.life:
                        if life < self.life:  # cannot win life except cheating
                            self.reward += self.delta_reward_by_life * (life - self.life)
                        self.life = life
                    level = body[2][13:15]
                    if len(level)>0:
                        level = int(body[2][13:15], 16)
                    else:
                        level = 0
                    # print("(from Python) level =", level)  # DEBUG
                    if level != self.level:
                        if level > self.level:  # cannot lose level
                            self.reward += self.delta_reward_by_level * (level - self.level)
                        self.level = level

    def _open_pipes(self):
        # emulator to client
        self.pipe_in_name = "/tmp/nesgym-pipe-{}-in".format(self._emulatornumber)
        self._ensure_create_pipe(self.pipe_in_name)
        # client to emulator
        self.pipe_out_name = "/tmp/nesgym-pipe-{}-out".format(self._emulatornumber)
        self._ensure_create_pipe(self.pipe_out_name)

        self.thread_incoming = Thread(
            target=self._pipe_handler,
            # name="/tmp/nesgym-pipe-{}-inout".format(self._emulatornumber),
        )
        self.thread_incoming.start()
        print("Using a thread of name {} and id {} (alive ? {})...".format(self.thread_incoming.name, self.thread_incoming.ident, self.thread_incoming.is_alive()))  # DEBUG

    def _ensure_create_pipe(self, pipe_name):
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)
    ## ------------ end pipes --------------
