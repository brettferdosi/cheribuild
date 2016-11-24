#
# Copyright (c) 2016 Alex Richardson
# All rights reserved.
#
# This software was developed by SRI International and the University of
# Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-10-C-0237
# ("CTSRD"), as part of the DARPA CRASH research programme.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
from ..project import CMakeProject, Project
from ..utils import *
from pathlib import Path
import tempfile

import os


def kdevInstallDir(config: CheriConfig):
    return config.sdkDir


class BuildLibKompareDiff2(CMakeProject):
    defaultCMakeBuildType = "Debug"

    def __init__(self, config: CheriConfig):
        super().__init__(config, installDir=kdevInstallDir(config), gitUrl="git://anongit.kde.org/libkomparediff2.git")


class BuildKDevplatform(CMakeProject):
    dependencies = ["libkomparediff2"]
    defaultCMakeBuildType = "Debug"

    def __init__(self, config: CheriConfig):
        super().__init__(config, installDir=kdevInstallDir(config), appendCheriBitsToBuildDir=True,
                         gitUrl="https://github.com/RichardsonAlex/kdevplatform.git")
        self.gitBranch = "cheri"
        self.configureArgs.append("-DBUILD_git=OFF")


class BuildKDevelop(CMakeProject):
    dependencies = ["kdevplatform", "llvm"]
    defaultCMakeBuildType = "Debug"

    def __init__(self, config: CheriConfig):
        super().__init__(config, installDir=kdevInstallDir(config), appendCheriBitsToBuildDir=True,
                         gitUrl="https://github.com/RichardsonAlex/kdevelop.git")
        # Tell kdevelop to use the CHERI clang
        self.configureArgs.append("-DLLVM_ROOT=" + str(self.config.sdkDir))
        # install the wrapper script that sets the right environment variables
        self.configureArgs.append("-DINSTALL_KDEVELOP_LAUNCH_WRAPPER=ON")
        self.gitBranch = "cheri"


class StartKDevelop(Project):
    target = "run-kdevelop"
    dependencies = ["kdevelop"]

    def __init__(self, config: CheriConfig):
        super().__init__(config)
        self._addRequiredSystemTool("cmake")
        self._addRequiredSystemTool("qtpaths")

    def process(self):
        kdevelopBinary = self.config.sdkDir / "bin/start-kdevelop.py"
        if not kdevelopBinary.exists():
            self.dependencyError("KDevelop is missing:", kdevelopBinary,
                                 installInstructions="Run `cheribuild.py kdevelop` or `cheribuild.py " +
                                                     self.target + " -d`.")
        runCmd(kdevelopBinary, "--ps")
