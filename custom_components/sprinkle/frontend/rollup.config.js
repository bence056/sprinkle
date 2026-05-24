import typescript from '@rollup/plugin-typescript';
import commonjs from "@rollup/plugin-commonjs";
import nodeResolve from "@rollup/plugin-node-resolve";

const plugins = [
  nodeResolve(),
  commonjs({
    include: 'node_modules/**'
  }),
  typescript()
];

export default
  {
    input: 'src/sprinkle-panel.ts',
    output: {
      dir: 'dist',
      format: 'iife',
      sourcemap: false
    },
    plugins: [...plugins],
    context: 'window'
  }