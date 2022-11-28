import { useState } from "react";
import styles from "./App.module.css";

const camelToCap = {
  pMax: "Pmax",
  pMin: "Pmin",
  a: "a",
  b: "b",
  c: "c",
  startingCost: "Starting Cost"
};

const generatorInput = {
  pMax: undefined,
  pMin: undefined,
  a: undefined,
  b: undefined,
  c: undefined,
  startingCost: undefined
};

const App = () => {
  const [loadCurve, setLoadCurve] = useState(Array(24).fill());
  const [generators, setGenerators] = useState([]);
  const [genInput, setGenInput] = useState(generatorInput);
  const [output, setOutput] = useState("");

  const addGenerator = () => {
    setGenerators([...generators, genInput]);
  };

  const deleteGenerator = idx => {
    setGenerators([...generators.slice(0, idx), ...generators.slice(idx + 1)]);
  };

  const compute = async () => {
    const generatorsArray = generators.map((gen, idx) => ({
      count: idx + 1,
      ...gen
    }));
    const data = {
      loads: loadCurve,
      generators: generatorsArray
    };
    console.log(data);
    const response = await fetch("http://localhost:5000/compute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });
    setOutput(await response.text());
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>PSECT Assignment</h1>
      <h3 className={styles.title}>Load curve values</h3>
      <div className={styles.loadCurve}>
        {loadCurve.map((val, idx) => (
          <div key={idx} className={styles.loadCurveInput}>
            <div>{idx + 1}</div>
            <input
              type={"number"}
              value={val}
              onChange={e => {
                setLoadCurve([
                  ...loadCurve.slice(0, idx),
                  Number(e.target.value),
                  ...loadCurve.slice(idx + 1)
                ]);
              }}
            />
          </div>
        ))}
      </div>
      <h3 className={styles.title}>Generator details</h3>
      <table>
        <thead>
          <tr>
            {[
              "Generator",
              "Pmax",
              "Pmin",
              "a",
              "b",
              "c",
              "Starting Cost",
              ""
            ].map(heading => (
              <th key={heading}>{heading}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {generators.length === 0 && (
            <tr>
              <td style={{ color: "gray" }} colSpan={8}>
                You have not added any generator data
              </td>
            </tr>
          )}
          {generators.map((gen, idx) => (
            <tr key={idx}>
              <td>{idx + 1}</td>
              {Object.keys(gen).map(key => (
                <td key={key}>{gen[key]}</td>
              ))}
              <td
                style={{ cursor: "pointer" }}
                onClick={() => deleteGenerator(idx)}
              >
                Del
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className={styles.addGen}>
        {Object.keys(generatorInput).map(key => (
          <div key={key} className={styles.genInput}>
            <div>{camelToCap[key]}</div>
            <input
              type={"number"}
              value={generatorInput[key]}
              onChange={e => {
                setGenInput({
                  ...genInput,
                  [key]: Number(e.target.value)
                });
              }}
            />
          </div>
        ))}
      </div>
      <button onClick={addGenerator} className={styles.addBtn}>
        Add Generator
      </button>
      <button onClick={compute} className={styles.compute}>
        Compute
      </button>
      {output !== "" && <h3 className={styles.outputTitle}>Output</h3>}
      <div className={styles.output}>{output}</div>
    </div>
  );
};

export default App;
