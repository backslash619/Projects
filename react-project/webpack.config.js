var path = require("path");

var DIST_DIR = path.resolve(__dirname, "dist");
var SRC_DIR = path.resolve(__dirname, "src");

module.exports =module.exports = {
    entry:SRC_DIR + "/app/index.js",
    output: {
        path: DIST_DIR+ "/app",
        filename: "bundle.js",
        publicPath: '/app/'
    },
    devServer: {
        noInfo: true,
        hot: true,
        inline: true
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                include : SRC_DIR,
                exclude:/(node_modules|bower_components)/,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015', 'react', "stage-2"]
                }
            }
        ]
    }

};
