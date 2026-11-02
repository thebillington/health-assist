import SwiftUI
import AppleHealthSyncCore

struct ContentView: View {
    private enum Field: Hashable {
        case webhook
        case secret
    }

    private enum Replacement {
        case scan
        case link(URL)
    }

    @StateObject private var model = AppModel()
    @StateObject private var tipJar = TipJarStore()
    @Environment(\.scenePhase) private var scenePhase
    @State private var showingScanner = false
    @State private var showingReplaceConfirmation = false
    @State private var pendingReplacement: Replacement?
    @FocusState private var focusedField: Field?

    var body: some View {
        NavigationStack {
            ScrollViewReader { _ in
                Form {
                    Section {
                        TextField("https://home.example.com/api/webhook/…", text: $model.webhookURL)
                            .keyboardType(.URL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .focused($focusedField, equals: .webhook)
                            .submitLabel(.done)
                            .onSubmit { focusedField = nil }

                        SecureField("Optional shared secret", text: $model.secret)
                            .textContentType(.password)
                            .autocorrectionDisabled()
                            .focused($focusedField, equals: .secret)
                            .submitLabel(.done)
                            .onSubmit { focusedField = nil }

                        Toggle("Sync when the app opens", isOn: $model.syncOnOpen)

                        Button {
                            requestScan()
                        } label: {
                            Label("Scan QR Code", systemImage: "qrcode.viewfinder")
                        }
                    } header: {
                        Text("Home Assistant")
                    } footer: {
                        Text("Create a webhook under Settings → Devices & services → Health Bridge. The full URL is a credential; keep it private.")
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
                        Text("Read-only access. The app never writes to Apple Health. iOS does not reveal which read permissions were granted; if values are missing, check Settings → Privacy & Security → Health → Health Bridge. Changing the additional-metrics option requires requesting access again.")
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
                        Text("Health Bridge sends data directly to your Home Assistant instance. It has no analytics, no telemetry and no cloud service. The webhook URL and shared secret are stored in the iOS Keychain.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }

                    Section {
                        if tipJar.isLoading {
                            HStack(spacing: 12) {
                                ProgressView()
                                    .controlSize(.small)
                                Text("Loading tip jar…")
                                    .foregroundStyle(.secondary)
                            }
                        } else if tipJar.products.isEmpty {
                            Text("The tip jar is not available right now.")
                                .foregroundStyle(.secondary)
                        } else {
                            ForEach(tipJar.products, id: \.id) { product in
                                Button {
                                    Task { await tipJar.purchase(product) }
                                } label: {
                                    HStack {
                                        Text(product.displayName)
                                        Spacer()
                                        Text(product.displayPrice)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                                .disabled(tipJar.isPurchasing)
                            }
                        }

                        if let message = tipJar.message {
                            Text(message)
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                        }
                    } header: {
                        Text("Tip Jar")
                    } footer: {
                        Text("Tips are optional and unlock nothing. The app is complete without them.")
                    }

                    Section {
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/privacy/")!) {
                            Label("Privacy Policy", systemImage: "hand.raised")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/terms/")!) {
                            Label("Terms of Use", systemImage: "doc.text")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/")!) {
                            Label("Documentation", systemImage: "book")
                        }
                        Link(destination: URL(string: "https://healthassist.thebillington.co.uk/install/")!) {
                            Label("HACS setup guide", systemImage: "wrench.and.screwdriver")
                        }
                    } header: {
                        Text("Links")
                    }
                }
                .scrollDismissesKeyboard(.interactively)
                .toolbar {
                    ToolbarItemGroup(placement: .keyboard) {
                        Spacer()
                        Button("Done") {
                            focusedField = nil
                        }
                        .fontWeight(.semibold)
                    }
                }
                .navigationTitle("Health Bridge")
                .onChange(of: model.webhookURL) { _, _ in model.saveSettings() }
                .onChange(of: model.secret) { _, _ in model.saveSettings() }
                .onChange(of: model.syncOnOpen) { _, _ in model.saveSettings() }
                .onChange(of: model.includeExtras) { _, _ in
                    model.saveSettings()
                    model.updateBackgroundDelivery()
                    Task { await model.refreshHealthStatus() }
                }
                .onOpenURL { url in
                    // A link from another app or the Camera must never replace
                    // credentials silently. Ask first if anything is set.
                    if hasDetails {
                        pendingReplacement = .link(url)
                        showingReplaceConfirmation = true
                    } else {
                        model.importConfiguration(from: url)
                    }
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
                    Button("Cancel", role: .cancel) {
                        pendingReplacement = nil
                    }
                    Button("Replace", role: .destructive) {
                        let replacement = pendingReplacement
                        pendingReplacement = nil
                        switch replacement {
                        case .some(.scan):
                            showingScanner = true
                        case .some(.link(let url)):
                            model.importConfiguration(from: url)
                        case .none:
                            break
                        }
                    }
                } message: {
                    Text("Importing new details will replace the current webhook URL and shared secret.")
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

    private var hasDetails: Bool {
        !model.webhookURL.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            || !model.secret.isEmpty
    }

    private func requestScan() {
        if hasDetails {
            pendingReplacement = .scan
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
