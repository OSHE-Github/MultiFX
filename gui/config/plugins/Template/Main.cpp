#include <JuceHeader.h>
#include "TemplatePlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TempProcessor();
}
