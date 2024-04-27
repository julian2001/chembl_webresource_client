
// swift-tools-version:5.3
import PackageDescription

let package = Package(
    name: "Vera",
    products: [
        .library(
            name: "Vera",
            targets: ["Vera"]),
    ],
    dependencies: [
        .package(url: "https://github.com/SwiftyJSON/SwiftyJSON.git", .upToNextMajor(from: "5.0.0")),
    ],
    targets: [
        .target(
            name: "Vera",
            dependencies: ["SwiftyJSON"]),
        .testTarget(
            name: "VeraTests",
            dependencies: ["Vera"]),
    ]
)
