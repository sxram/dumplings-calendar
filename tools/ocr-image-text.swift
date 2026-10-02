import Foundation
import Vision
import AppKit
var output: [[String: Any]] = []
for path in CommandLine.arguments.dropFirst() {
 let url = URL(fileURLWithPath: path)
 let req = VNRecognizeTextRequest()
 req.recognitionLevel = .accurate
 req.recognitionLanguages = ["de-DE", "en-US"]
 req.usesLanguageCorrection = false
 try VNImageRequestHandler(url: url).perform([req])
 let rep = NSBitmapImageRep(data: try Data(contentsOf: url))!
 let w = Double(rep.pixelsWide), h = Double(rep.pixelsHigh)
 let lines: [[String: Any]] = (req.results ?? []).compactMap { obs in
  guard let text = obs.topCandidates(1).first?.string else { return nil }
  let b = obs.boundingBox
  return ["text":text,"box":[b.minX*w,(1-b.maxY)*h,b.maxX*w,(1-b.minY)*h]]
 }
 output.append(["path":path,"size":[w,h],"lines":lines])
}
let data=try JSONSerialization.data(withJSONObject:output,options:[.prettyPrinted,.sortedKeys])
FileHandle.standardOutput.write(data)
