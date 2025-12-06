#include <JuceHeader.h>
#include "CompressionPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new CompressionProcessor();
}
