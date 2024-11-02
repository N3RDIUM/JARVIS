let pkgs = import <nixpkgs> { };
in pkgs.mkShell {
    packages = [
        (pkgs.python3.withPackages (python-pkgs: [
            python-pkgs.torch
            python-pkgs.ollama
            python-pkgs.google-search-results
            python-pkgs.faster-whisper
            python-pkgs.speechrecognition
        ]))
    ];
    buildInputs = [ pkgs.libz ];
}
