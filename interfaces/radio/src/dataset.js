function get_dataset(name) {
  // dataset size
  let n = -1;

  // check if the dataset name is correct
  // then assign the correct dataset size
  switch (name) {
    case "dogs3":
      n = 473;
      break;
    case "birds5":
      n = 342
      break;
    default:
      throw new Error(`The dataset '${name}' does not exist`);
  }

  const urls = [];
  const base_url = `https://d1wjx6kuxoi8by.cloudfront.net/${name}/`;

  for (let i = 0; i < n; i++) {
    urls.push(base_url + `${i}.jpg`);
  }

  return urls;
}

export default get_dataset;