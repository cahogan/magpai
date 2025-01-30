import typescript from "@rollup/plugin-typescript"
import glob from "glob"
import * as path from "path"

// Find all page.ts files in the project
// Assumes that page.ts files are in a folder namespaced by the page name
// We can filter for a particular page to speed up build times
function getEntryPoints(pageName = undefined) {
  let pageFilter = "**/page.ts"
  if (pageName) {
    console.log(`Building ${pageName}`)
    pageFilter = `**/${pageName}/page.ts`
  }
  const entryPoints = glob.sync(pageFilter).map((file) => {
    const { dir } = path.parse(file)
    const pagesParentDir = path.dirname(dir)
    const pageDir = path.basename(dir)
    const builtFilePath = path.join(
      pagesParentDir,
      "built",
      pageDir + ".js"
    )
    return [file, builtFilePath]
  })
  return entryPoints
}

const plugins = [typescript()]

function createConfig(entryPoints) {
  const rollupConfig = entryPoints.map(([inputFilePath, outputFilePath]) => {
    return {
      input: inputFilePath,
      output: {
        file: outputFilePath,
        format: "cjs",
        sourcemap: true,
      },
      plugins,
    }
  })
  return rollupConfig
}

// Users can specify configEntrypointFile to filter page to build
// example: npm run build -- --configEntrypointFile game will build any 'game' pages only
export default commandLineArgs => {
  const entryPoints = getEntryPoints(commandLineArgs.configEntrypointFile)
  return createConfig(entryPoints)
}
