import SwiftUI
import AppleHealthSyncCore

struct ContentView: View {
    @StateObject private var model = AppModel()
    @Environment(\.scenePhase) private var scenePhase
    @State private var showingScanner = false
    @State private var showingReplaceConfirmation = false

    var body: some View {
        NavigationStack {
            ScrollViewReader { _ in
                Form {
                    Section {
                        TextField("https://home.example.com/api/webhook/…", text: $model.webhookURL)
                            .keyboardType(.URL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        SecureField("Optional shared secret", text: $model.secret)
                            .textContentType(.password)
                            .autocorrectionDisabled()

                        Toggle("Sync when the app opens", isOn: $model.syncOnOpen)

                        Button {
                            requestScan()
                        } label: {
                            Label("Scan QR Code", systemImage: "qrcode.viewfinder")
                        }
                    } header: {
                        Text("Home Assistant")
                    } footer: {
                        Text("Create a webhook under Settings → Devices & services → Health Sync. The full URL is a credential; keep it private.")
                    }

                    Section {
                        HStack {
                            Text("Status")
                            Spacer()
                            Text(model.healthStatus)
                                .foregroundStyle(.secondary)
                        }

                        Button {
                            Task { await model.requestHealthAccess() }
                        } label: {
                            HStack {
                                Text("Request Health Access")
                                Spacer()
                                if model.isRequestingAccess {
                                    ProgressView()
                                }
                            }
                        }
                        .disabled(model.isRequestingAccess)

                        Toggle("Include additional HealthKit metrics", isOn: $model.includeExtras)
                    } header: {
                        Text("Apple Health")
                    } footer: {
                        Text("Read-only access. The app never writes to Apple Health. iOS does not reveal which read permissions were granted; if values are missing, check Settings → Privacy & Security → Health → Health Sync. Changing the additional-metrics option requires requesting access again.")
                    }

                    Section {
                        Button {
                            Task { await model.sync() }
                        } label: {
                            HStack(spacing: 8) {
                                if model.isSyncing {
                                    ProgressView()
                                        .controlSize(.small)
                                }
                                Text(model.isSyncing ? "Syncing…" : "Sync Now")
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .disabled(model.isSyncing)

                        Button("Send a Test Payload") {
                            Task { await model.sendTestPayload() }
                        }
                        .disabled(model.isSyncing)

                        Button("Re-export All History") {
                            Task { await model.reexportAllHistory() }
                        }
                        .disabled(model.isSyncing)
                    } header: {
                        Text("Sync")
                    } footer: {
                        Text("The first sync exports your full HealthKit history in resumable chunks, then keeps it up to date. The test payload uses fixed sample values and works without HealthKit, including in the iOS simulator. On a physical iPhone, background delivery syncs hourly and a weekly fallback is scheduled when iOS allows it.")
                    }

                    Section {
                        Text(model.statusMessage)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .textSelection(.enabled)

                        if let lastSync = model.lastSync {
                            HStack {
                                Text("Last successful sync")
                                Spacer()
                                Text(lastSync, format: .dateTime.day().month().year().hour().minute())
                                    .foregroundStyle(.secondary)
                            }
                            .font(.footnote)
                        }

                        if let lastBackgroundSync = model.lastBackgroundSync {
                            HStack {
                                Text("Last background sync")
                                Spacer()
                                Text(lastBackgroundSync, format: .dateTime.day().month().year().hour().minute())
                                    .foregroundStyle(.secondary)
                            }
                            .font(.footnote)
                        }
                    } header: {
                        Text("Result")
                    }
                    .id("result")

                    Section("Latest Values") {
                        if model.readings.isEmpty {
                            Text("No values yet. Sync once to populate this list.")
                                .foregroundStyle(.secondary)
                        } else {
                            ForEach(model.readings) { reading in
                                HStack(alignment: .firstTextBaseline) {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(reading.name)
                                        if !reading.canonical {
                                            Text("Additional metric")
                                                .font(.caption2)
                                                .foregroundStyle(.secondary)
                                        }
                                    }

                                    Spacer()

                                    Text(formatted(reading.value))
                                        .monospacedDigit()

                                    if let unit = reading.unit {
                                        Text(unit)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                    }

                    Section {
                        Text("Health Sync sends data directly to your Home Assistant instance. It has no analytics, no telemetry and no cloud service. The webhook URL and shared secret are stored in the iOS Keychain.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }

                    Section {
                        Link(destination: URL(string: "https://github.com/sponsors/thebillington")!) {
                            Label("Support Me", systemImage: "heart")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/privacy/")!) {
                            Label("Privacy Policy", systemImage: "hand.raised")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/")!) {
                            Label("Documentation", systemImage: "book")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/install/")!) {
                            Label("HACS setup guide", systemImage: "wrench.and.screwdriver")
                        }
                        Text("If you want to support my work, click the Support Me button. It opens GitHub Sponsors and unlocks no features.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    } header: {
                        Text("Support")
                    }
                }
                .navigationTitle("Health Sync")
                .onChange(of: model.webhookURL) { _, _ in model.saveSettings() }
                .onChange(of: model.secret) { _, _ in model.saveSettings() }
                .onChange(of: model.syncOnOpen) { _, _ in model.saveSettings() }
                .onChange(of: model.includeExtras) { _, _ in
                    model.saveSettings()
                    model.updateBackgroundDelivery()
                    Task { await model.refreshHealthStatus() }
                }
                .onOpenURL { url in
                    model.importConfiguration(from: url)
                }
                .sheet(isPresented: $showingScanner) {
                    QRScannerView { code in
                        showingScanner = false
                        model.importConfiguration(fromCode: code)
                    }
                    .ignoresSafeArea()
                }
                .alert(
                    "Replace Home Assistant details?",
                    isPresented: $showingReplaceConfirmation
                ) {
                    Button("Cancel", role: .cancel) {}
                    Button("Replace", role: .destructive) {
                        showingScanner = true
                    }
                } message: {
                    Text("Scanning a QR code will replace the current webhook URL and shared secret.")
                }
                .task { await model.prepare() }
                .onChange(of: scenePhase) { _, newPhase in
                    if newPhase == .active {
                        model.refreshBackgroundSyncDate()
                        Task { await model.syncOnLaunchIfNeeded() }
                    }
                }
            }
        }
    }

    private func requestScan() {
        let hasDetails = !model.webhookURL.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            || !model.secret.isEmpty
        if hasDetails {
            showingReplaceConfirmation = true
        } else {
            showingScanner = true
        }
    }

    private func formatted(_ value: Double) -> String {
        if value == value.rounded() {
            return String(Int(value))
        }
        return value.formatted(.number.precision(.fractionLength(0...2)))
    }
}

#Preview {
    ContentView()
}
