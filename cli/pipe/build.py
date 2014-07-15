import os.path as op
import shutil

from cli.system import stdoutlog, run, prun, shutil as shellutil
from scripts.font2ttf import convert


class Build(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.stdout_pipe = stdout_pipe
        self.project_root = project_root
        self.builddir = builddir

    def otf2ttf(self, filepath):
        _ = '$ font2ttf.py {0}.otf {0}.ttf\n'
        fontname = filepath[:-4]

        self.stdout_pipe.write(_.format(fontname))
        try:
            path = '{}.otf'.format(fontname)
            ttfpath = '{}.ttf'.format(fontname)
            convert(path, ttfpath, log=self.stdout_pipe)
            shellutil.remove(path, log=self.stdout_pipe)
        except Exception, ex:
            self.stdout_pipe.write('Error: %s\n' % ex.message)
            raise

    def movebin_to_builddir(self, project_root, builddir, files):
        result = []
        for a in files:
            d = op.join(project_root, builddir, op.basename(a)[:-4] + '.ttf')
            s = op.join(project_root, builddir, a[:-4] + '.ttf')

            shutil.move(s, d)
            result.append(d)
        return result

    def execute(self, pipedata):
        ttx = []
        ufo = []
        sfd = []
        bin = []
        for p in pipedata['process_files']:
            if p.endswith('.ttx'):
                ttx.append(p)
            elif p.endswith('.sfd'):
                sfd.append(p)
            elif p.endswith('.ufo'):
                ufo.append(p)
            elif p.endswith('.ttf'):
                bin.append(p)
            elif p.endswith('.otf'):
                bin.append(p)

        self.stdout_pipe.write('Convert sources to TTF\n', prefix="### ")
        if ttx:
            self.execute_ttx(self.project_root, self.builddir, ttx)
        if ufo:
            self.execute_ufo_sfd(self.project_root, self.builddir, ufo)
        if sfd:
            self.execute_ufo_sfd(self.project_root, self.builddir, sfd)
        if bin:
            self.execute_bin(self.project_root, self.builddir, bin)

        binfiles = self.movebin_to_builddir(self.project_root, self.builddir, ufo + ttx + sfd + bin)

        SCRIPTPATH = op.join('scripts', 'fix-ttf-vmet.py')
        command = ' '.join(binfiles)
        prun('python %s %s' % (SCRIPTPATH, command),
             cwd=op.abspath(op.join(op.dirname(__file__), '..', '..')),
             log=self.stdout_pipe)

        pipedata['bin_files'] = binfiles

        return pipedata

    def execute_ttx(self, project_root, builddir, files):
        paths = []
        for f in files:
            f = op.join(project_root, builddir, f)
            paths.append(f)

        run("ttx {}".format(' '.join(paths)), cwd=builddir,
            log=self.stdout_pipe)

        for p in files:
            self.otf2ttf(p)

    def execute_ufo_sfd(self, project_root, builddir, files):
        for f in files:
            filepath = op.join(builddir, f)
            _ = '$ font2ttf.py %s %s'
            self.stdout_pipe.write(_ % (filepath,
                                        filepath[:-4] + '.ttf'))
            ttfpath = filepath[:-4] + '.ttf'

            try:
                convert(filepath, ttfpath, log=self.stdout_pipe)
            except Exception, ex:
                self.stdout_pipe.write('# Error: %s\n' % ex.message)

    def execute_bin(self, project_root, builddir, files):
        for p in files:
            if p.endswith('.otf'):
                self.otf2ttf(p)
