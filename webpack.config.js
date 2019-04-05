const WEBPACK_MODE = process.env.NODE_ENV === 'development' ? 'development' : 'production';

const path = require('path');
const fs = require('fs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const ShortHandBabelPlugin = require('babel-plugin-transform-es2015-shorthand-properties');
const WebpackNotifierPlugin = require('webpack-notifier');


let plugins = [
    new MiniCssExtractPlugin({
        filename: '../css/style.css',
    }),
    {
        apply: (compiler) => {
        compiler.plugin('done', (stats) => {
        stats = stats.toJson();
let dir = path.join(__dirname, 'frontend/build');
if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, 0o0740);
}
let manifest = Object.keys(stats.entrypoints).reduce(function (manifest, entrypointName) {
    let chunkIds = stats.entrypoints[entrypointName].chunks;
    // concat all chunk hashes and write to entry point key in manifest
    manifest[entrypointName] = chunkIds.reduce(function (chunkHashString, nextChunkId) {
        let chunksById = stats.chunks.filter(chunk => chunk.id === nextChunkId);
        if (chunksById.length) {
            return chunkHashString + chunksById[0].hash;
        } else {
            return chunkHashString
        }
    }, '');
    return manifest;
}, {});
fs.writeFileSync(
    path.join(dir, 'assets.json'),
    JSON.stringify(manifest)
);
});
}
}
];
if (WEBPACK_MODE === 'development') {
    plugins.push(new WebpackNotifierPlugin({title: 'Webpack build...', alwaysNotify: true, sourceMap: true}))
}

module.exports = {
    entry: {
        script: './frontend/js/script.js',
    },
    output: {
        filename: '[name].js',
        path: path.join(__dirname, '/static/js'),
        sourceMapFilename: '[name].js.map',
        publicPath: '/'
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                cache: true,
                parallel: true,
                sourceMap: true // set to true if you want JS source maps
            }),
            new OptimizeCSSAssetsPlugin({})
        ]
    },
    devtool: (WEBPACK_MODE === 'development') ? 'cheap-module-source-map' : 'nosources-source-map',
    module: {
        rules: [
            //vue loader
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            // babel-loader
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['env'],
                        plugins: [ShortHandBabelPlugin]
                    }
                }
            },
            // sass-loader
            {
                test: /\.s?[ac]ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader'
                ],
            },
            // font loader
            {
                test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: '[name].[ext]',
                        outputPath: '../fonts/'
                    }
                }]
            }
        ],
    },
    resolve: {
        alias: {
            vue: 'vue/dist/vue.js'
        },
    },
    plugins: plugins
};
