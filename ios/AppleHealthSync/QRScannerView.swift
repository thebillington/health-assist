import SwiftUI
import VisionKit

/// Full-screen QR scanner backed by VisionKit's DataScannerViewController.
struct QRScannerView: UIViewControllerRepresentable {
    let onCode: (String) -> Void

    func makeUIViewController(context: Context) -> UIViewController {
        let controller = ScannerHostController(onCode: onCode)
        controller.modalPresentationStyle = .fullScreen
        return controller
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}

    final class ScannerHostController: UIViewController, DataScannerViewControllerDelegate {
        private let onCode: (String) -> Void
        private var scanner: DataScannerViewController?
        private var reported = false

        init(onCode: @escaping (String) -> Void) {
            self.onCode = onCode
            super.init(nibName: nil, bundle: nil)
        }

        @available(*, unavailable)
        required init?(coder: NSCoder) {
            fatalError("init(coder:) has not been implemented")
        }

        override func viewDidLoad() {
            super.viewDidLoad()
            view.backgroundColor = .black

            guard DataScannerViewController.isSupported,
                  DataScannerViewController.isAvailable else {
                let label = UILabel()
                label.text = "Camera QR scanning is not available on this device."
                label.textColor = .white
                label.textAlignment = .center
                label.numberOfLines = 0
                label.translatesAutoresizingMaskIntoConstraints = false
                view.addSubview(label)
                NSLayoutConstraint.activate([
                    label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 24),
                    label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -24),
                    label.centerYAnchor.constraint(equalTo: view.centerYAnchor),
                ])
                return
            }

            let scanner = DataScannerViewController(
                recognizedDataTypes: [.barcode(symbologies: [.qr])],
                qualityLevel: .balanced,
                recognizesMultipleItems: false,
                isHighFrameRateTrackingEnabled: false,
                isPinchToZoomEnabled: true,
                isGuidanceEnabled: true,
                isHighlightingEnabled: true
            )
            scanner.delegate = self
            self.scanner = scanner

            addChild(scanner)
            scanner.view.frame = view.bounds
            scanner.view.autoresizingMask = [.flexibleWidth, .flexibleHeight]
            view.addSubview(scanner.view)
            scanner.didMove(toParent: self)
        }

        override func viewDidAppear(_ animated: Bool) {
            super.viewDidAppear(animated)
            try? scanner?.startScanning()
        }

        override func viewWillDisappear(_ animated: Bool) {
            scanner?.stopScanning()
            super.viewWillDisappear(animated)
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didAdd addedItems: [RecognizedItem],
            allItems: [RecognizedItem]
        ) {
            reportFirstCode(in: addedItems)
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didTapOn item: RecognizedItem
        ) {
            report(item)
        }

        private func reportFirstCode(in items: [RecognizedItem]) {
            for item in items {
                if report(item) {
                    return
                }
            }
        }

        @discardableResult
        private func report(_ item: RecognizedItem) -> Bool {
            guard !reported,
                  case let .barcode(barcode) = item,
                  let payload = barcode.payloadStringValue else {
                return false
            }
            reported = true
            scanner?.stopScanning()
            onCode(payload)
            return true
        }
    }
}
