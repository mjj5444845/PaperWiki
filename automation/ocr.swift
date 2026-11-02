// Read-only OCR of supplied page images; never captures the screen or opens UI.
import Foundation
import Vision
var result: [String: [[String: Any]]] = [:]
for name in CommandLine.arguments.dropFirst() {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]
    do {
        try VNImageRequestHandler(url: URL(fileURLWithPath: name), options: [:]).perform([request])
        result[name] = (request.results ?? []).compactMap { observation in
            guard let candidate = observation.topCandidates(1).first, candidate.confidence >= 0.5 else { return nil }
            return ["text": candidate.string, "confidence": candidate.confidence]
        }
    } catch {
        fputs("OCR failed for supplied image: \(error)\n", stderr)
        exit(1)
    }
}
let output = try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
FileHandle.standardOutput.write(output)
