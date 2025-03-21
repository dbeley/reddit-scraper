with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell {
  buildInputs = [
    pythonPackages.python

    pythonPackages.praw
    pythonPackages.pandas
    pythonPackages.tqdm
    pythonPackages.black
    pythonPackages.xlsxwriter
  ];

}
