// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "AppleHealthSyncCore",
    platforms: [
        .iOS(.v18),
        .macOS(.v13),
    ],
    products: [
        .library(name: "AppleHealthSyncCore", targets: ["AppleHealthSyncCore"]),
    ],
    targets: [
        .target(name: "AppleHealthSyncCore"),
        .testTarget(
            name: "AppleHealthSyncCoreTests",
            dependencies: ["AppleHealthSyncCore"]
        ),
    ]
)
