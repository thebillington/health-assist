import SwiftUI

@main
struct AppleHealthSyncApp: App {
    init() {
        let includeExtras = SettingsStore().includeExtras
        Task { @MainActor in
            BackgroundSyncManager.shared.start(
                includeExtras: includeExtras,
                force: true
            )
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .backgroundTask(.appRefresh(BackgroundSyncManager.weeklyTaskIdentifier)) {
            await BackgroundSyncManager.shared.performWeeklySync()
        }
    }
}
